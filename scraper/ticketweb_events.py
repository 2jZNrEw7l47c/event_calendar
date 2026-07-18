"""Shared helper for WordPress sites using the TicketWeb event plugin
(Belly Up, Brick By Brick, The Sound). Events are rendered server-side as rows
with `tw-` classes: `.tw-event-date-complete` (e.g. "Jul 17"), `.tw-headliner`
for the act(s), `.tw-support` for openers, and a ticketweb.com ticket link.

Rows don't include a start time, so we default to 20:00 (typical show time);
the year isn't printed either, so it's inferred like the other text venues.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common


def scrape_ticketweb(url, venue, category, today=None, default_time="20:00"):
    today = today or datetime.date.today()
    resp = requests.get(url, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for dcomp in soup.select(".tw-event-date-complete"):
        # container = nearest ancestor that also holds the ticket link
        cont = dcomp
        for _ in range(6):
            cont = cont.parent
            if cont is None:
                break
            if cont.select_one("a[href*='ticketweb']"):
                break
        if cont is None:
            continue

        m = re.search(r"([A-Za-z]+)\s+(\d{1,2})", dcomp.get_text(" ", strip=True))
        if not m:
            continue
        month = common.month_to_num(m.group(1))
        if not month:
            continue
        d = common.infer_date(month, int(m.group(2)), today)
        if not d:
            continue

        heads = [a.get_text(" ", strip=True) for a in cont.select(".tw-headliner")]
        heads = [h for h in heads if h]
        if not heads:
            # event-discovery plugin variant uses .tw-name; older uses .tw-artist
            alt = cont.select_one(".tw-name") or cont.select_one(".tw-artist")
            if alt:
                heads = [alt.get_text(" ", strip=True)]
        title = ", ".join(dict.fromkeys(heads)) or "(untitled)"

        # Some variants include a door time ("Doors: 8:00 pm"); use it if present.
        door = cont.select_one(".tw-event-door-time")
        clock = common.parse_clock(door.get_text(" ", strip=True)) if door else None

        link = cont.select_one("a[href*='ticketweb']")
        ticket = link["href"] if link and link.has_attr("href") else None
        event_id = None
        if ticket:
            mid = re.search(r"/(\d+)(?:\?|$)", ticket)
            event_id = mid.group(1) if mid else None

        support = cont.select_one(".tw-support")
        description = support.get_text(" ", strip=True) if support else ""

        key = (d.isoformat(), title.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "%s-%s" % (category, event_id or (d.isoformat() + "-" + re.sub(r"[^a-z0-9]+", "-", title.lower())[:30])),
            "title": title,
            "date": d.isoformat(),
            "time": clock or default_time,
            "venue": venue,
            "category": category,
            "price": "",
            "description": description,
            "url": ticket or url,
        })
    return events
