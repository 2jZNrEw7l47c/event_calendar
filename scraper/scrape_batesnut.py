"""Bates Nut Farm, Valley Center (batesnutfarm.biz) — Shopify pages/events.

Server-rendered items: .event-item__details holding the title text, a
"Date: Saturday, July 18, 2026" paragraph (ranges use the first date), and an
optional "Time: 4:00pm - 8:00pm" line.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://batesnutfarm.biz/pages/events"


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for item in soup.select(".event-item__details"):
        dp = item.select_one(".event-item__date")
        if not dp:
            continue
        dtext = dp.get_text(" ", strip=True)
        m = re.search(r"([A-Za-z]+)\s+(\d{1,2})(?:\s*[-–]|,)?.*?(\d{4})", dtext)
        if not m:
            continue
        month = common.month_to_num(m.group(1))
        if not month:
            continue
        try:
            d = datetime.date(int(m.group(3)), month, int(m.group(2)))
        except ValueError:
            continue
        if d < today:
            continue

        full = item.get_text(" ", strip=True)
        title = full.split("Date:")[0].strip(" |")
        if not title:
            continue

        tm_ = re.search(r"Time:\s*([^L]+?)(?:Learn|$)", full)
        clock = common.parse_loose_time(tm_.group(1)) if tm_ else None

        a = item.find("a", href=True)
        url = a["href"] if a else URL
        if url.startswith("/"):
            url = "https://batesnutfarm.biz" + url

        key = (d.isoformat(), title.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "batesnut-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:30]),
            "title": title,
            "date": d.isoformat(),
            "time": clock or "10:00",
            "venue": "Bates Nut Farm",
            "category": "batesnut",
            "price": "",
            "description": (tm_.group(0).strip() if tm_ else ""),
            "url": url,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Bates Nut Farm: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
