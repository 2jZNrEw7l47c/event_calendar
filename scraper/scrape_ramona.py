"""Ramona Mainstage (ramonamainstage.com).

The homepage lists shows as anchors: "Saturday, July 18 · Struggle Jennings".
No year (inferred) and no time (default 20:00); the anchor href is the event
page.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://ramonamainstage.com"

_ROW = re.compile(r"^([A-Za-z]+),\s*([A-Za-z]+)\s+(\d{1,2})\s*[·•]\s*(.+)$")


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for a in soup.find_all("a"):
        m = _ROW.match(a.get_text(" ", strip=True))
        if not m:
            continue
        month = common.month_to_num(m.group(2))
        if not month:
            continue
        d = common.infer_date(month, int(m.group(3)), today)
        if not d or d < today:
            continue
        title = m.group(4).strip()

        url = a.get("href") or URL
        if url.startswith("/"):
            url = URL + url

        key = (d.isoformat(), title.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "ramona-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:30]),
            "title": title,
            "date": d.isoformat(),
            "time": "20:00",
            "venue": "Ramona Mainstage",
            "category": "ramona",
            "price": "",
            "description": "",
            "url": url,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Ramona: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
