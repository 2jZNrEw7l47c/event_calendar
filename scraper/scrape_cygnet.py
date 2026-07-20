"""Cygnet Theatre — The Joan at Liberty Station (cygnettheatre.org).

/shows-calendar server-renders a month table; each day cell has a
.shows-container-popup with the date ("Wednesday, July 01, 2026"), the show
title, and one or more curtain times. We emit one event per show per day,
using the first listed time. Past days carry a .past-date class we skip.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://cygnettheatre.org/shows-calendar"

_DATE = re.compile(r"([A-Za-z]+),\s*([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})")
_TIME = re.compile(r"^\d{1,2}:\d{2}\s*[ap]m$", re.I)


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=40)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for popup in soup.select(".shows-container-popup"):
        cell = popup.find_parent("td")
        if cell and "past-date" in " ".join(cell.get("class", [])):
            continue
        date_el = popup.select_one(".shows-date")
        if not date_el:
            continue
        m = _DATE.search(date_el.get_text(" ", strip=True))
        if not m:
            continue
        month = common.month_to_num(m.group(2))
        if not month:
            continue
        try:
            d = datetime.date(int(m.group(4)), month, int(m.group(3)))
        except ValueError:
            continue
        if d < today:
            continue

        link = popup.find("a", href=True)
        url = link["href"] if link else URL

        # walk the popup's text pieces: non-time text after the date is a show
        # title; time pieces belong to the most recent title.
        title = None
        for piece in popup.stripped_strings:
            if _DATE.search(piece):
                continue
            if _TIME.match(piece.strip()):
                if title:
                    key = (d.isoformat(), title.lower())
                    if key not in seen:
                        seen.add(key)
                        events.append({
                            "id": "cygnet-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:30]),
                            "title": title,
                            "date": d.isoformat(),
                            "time": common.parse_clock(piece) or "19:30",
                            "venue": "Cygnet Theatre",
                            "category": "cygnet",
                            "price": "",
                            "description": "",
                            "url": url,
                        })
            else:
                t = piece.strip()
                if len(t) > 2:
                    title = t
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Cygnet: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
