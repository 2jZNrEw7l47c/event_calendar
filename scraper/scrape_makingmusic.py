"""Museum of Making Music, Carlsbad (museumofmakingmusic.org/events).

Server-rendered teaser items: <div class="teaser-item event"> holding a
<div class="element-date"> ("Thursday, July 30, 2026 @ 7:00 PM (Pacific)"),
the title in the item's heading/link, and prices in the description block.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.museumofmakingmusic.org/events"


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for item in soup.select("div.teaser-item"):
        dt = item.select_one(".element-date")
        if not dt:
            continue
        text = dt.get_text(" ", strip=True)
        m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", text)
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
        clock = common.parse_clock(text) or "19:00"

        head = item.find(["h2", "h3", "h4"]) or item.find("a")
        title = head.get_text(" ", strip=True) if head else ""
        if not title:
            continue

        a = item.find("a", href=True)
        url = a["href"] if a else URL
        if url.startswith("/"):
            url = "https://www.museumofmakingmusic.org" + url

        price = ""
        pm = re.search(r"\$\d+[^\s]*", item.get_text(" ", strip=True))
        if pm:
            price = pm.group(0).rstrip(".,")

        key = (d.isoformat(), title.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "makingmusic-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:30]),
            "title": title,
            "date": d.isoformat(),
            "time": clock,
            "venue": "Museum of Making Music",
            "category": "makingmusic",
            "price": price,
            "description": "",
            "url": url,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Making Music: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
