"""SOMA (somasandiego.com) — all-ages venue with Mainstage + Sidestage.

The /events/ page is server-rendered WordPress: each show is an
<li class="event-onsale"> (or "event-soldout") with month/day/year spans, the
title in .event-info h3, and a stage + time string in .event-time (e.g.
"Sidestage - 7pm", "Doors 7pm - Mainstage"). Sold-out shows are skipped via the
li class. The year is printed, so no inference needed.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.somasandiego.com/events/"


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    for li in soup.select("li[class*=event-]"):
        cls = " ".join(li.get("class", []))
        if "event-soldout" in cls:
            continue

        month = common.month_to_num((li.select_one(".event-month") or li).get_text(strip=True))
        day_el = li.select_one(".event-day")
        year_el = li.select_one(".event-year")
        if not (month and day_el and year_el):
            continue
        try:
            d = datetime.date(int(year_el.get_text(strip=True)), month,
                              int(day_el.get_text(strip=True)))
        except ValueError:
            continue
        if d < today:
            continue

        h3 = li.select_one(".event-info h3 a") or li.select_one(".event-info h3")
        if not h3:
            continue
        title = h3.get_text(" ", strip=True)

        time_el = li.select_one(".event-time")
        time_text = time_el.get_text(" ", strip=True) if time_el else ""
        clock = common.parse_clock(time_text) or "19:00"

        ticket = li.select_one("a.event-tickets")
        info = li.select_one(".event-info h3 a")
        url = (ticket["href"] if ticket and ticket.has_attr("href") else None) \
            or (info["href"] if info and info.has_attr("href") else URL)

        events.append({
            "id": "soma-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:34]),
            "title": title,
            "date": d.isoformat(),
            "time": clock,
            "venue": "SOMA",
            "category": "soma",
            "price": "",
            "description": time_text,   # includes the stage, e.g. "Sidestage - 7pm"
            "url": url,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("SOMA: %d events" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["description"][:30])
