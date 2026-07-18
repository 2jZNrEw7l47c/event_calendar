"""The Tower Bar (thetowerbar.com) — WordPress with an Events Manager table.

The homepage (and /calendar) server-renders the schedule as a plain table:
    | 07/19/2026 8:00 pm - 11:45 pm | Echo Chamber - DJ Bloodline |
Dates are numeric with the year included, so parsing is direct.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.thetowerbar.com/"

_DATE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for row in soup.select("table tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        when = cells[0].get_text(" ", strip=True)
        title = cells[1].get_text(" ", strip=True)
        m = _DATE.search(when)
        if not m or not title:
            continue
        try:
            d = datetime.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError:
            continue
        if d < today:
            continue
        clock = common.parse_clock(when) or "20:00"

        link = cells[1].find("a")
        url = link["href"] if link and link.has_attr("href") else URL
        if url.startswith("/"):
            url = "https://www.thetowerbar.com" + url

        key = (d.isoformat(), title.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "towerbar-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:34]),
            "title": title,
            "date": d.isoformat(),
            "time": clock,
            "venue": "Tower Bar",
            "category": "towerbar",
            "price": "",
            "description": "",
            "url": url,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Tower Bar: %d events" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], e["time"], "-", e["title"][:60])
