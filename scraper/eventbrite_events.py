"""Shared helper for venues that sell through Eventbrite (SPIN, 710 Beach Club).

The venue page links to eventbrite.com/e/... pages; each of those pages embeds
schema.org JSON-LD server-side, so we collect the links and pull each event's
LD. Capped at MAX_EVENTS fetches per venue to stay polite.
"""

import re
import datetime

import requests

import common
import ld_events

MAX_EVENTS = 12

_EB_LINK = re.compile(r"https://www\.eventbrite\.com/e/[a-z0-9\-]+", re.I)


def scrape_eventbrite(page_url, venue, category, today=None):
    today = today or datetime.date.today()
    resp = requests.get(page_url, headers=common.UA, timeout=30)
    resp.raise_for_status()
    links = list(dict.fromkeys(_EB_LINK.findall(common.decode(resp))))[:MAX_EVENTS]

    events = []
    seen = set()
    for link in links:
        try:
            er = requests.get(link, headers=common.UA, timeout=30)
            if er.status_code != 200:
                continue
            page = common.decode(er)
        except requests.RequestException:
            continue
        for e in ld_events.extract_ld_events(page):
            name = (e.get("name") or "").strip()
            d, tm = ld_events.parse_start(e.get("startDate"))
            if not name or not d or d < today.isoformat():
                continue
            key = (d, name.lower())
            if key in seen:
                continue
            seen.add(key)
            events.append({
                "id": "%s-%s-%s" % (category, d, re.sub(r"[^a-z0-9]+", "-", name.lower())[:32]),
                "title": name,
                "date": d,
                "time": tm or "21:00",
                "venue": venue,
                "category": category,
                "price": ld_events._price(e.get("offers")),
                "description": "",
                "url": link,
            })
    return events
