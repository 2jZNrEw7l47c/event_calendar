"""Moonshine Beach + Moonshine Flats (moonshinebeachsd.com) — uv-calendar.

The Beach site's /calendar/ renders a "uv-calendar" widget server-side whose
event links encode everything we need:

    /event/?id=1754703&dt=260714&ve=beach   (dt = YYMMDD, ve = beach|flats)

with the title in a sibling <div class='name'>. One page covers BOTH venues,
so this module exposes two scrape functions sharing one fetch.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://moonshinebeachsd.com/calendar/"

_VENUES = {
    "beach": ("Moonshine Beach", "moonshinebeach"),
    "flats": ("Moonshine Flats", "moonshineflats"),
}

_LINK = re.compile(r"[?&]id=(\d+).*?[?&]?dt=(\d{6}).*?[?&]ve=(beach|flats)")


def _fetch_all(today):
    resp = requests.get(URL, headers=common.UA, timeout=40)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = {"beach": [], "flats": []}
    seen = set()
    for a in soup.select("a[href*='/event/?id=']"):
        m = _LINK.search(a["href"])
        name_el = a.select_one("div.name")
        if not m or not name_el:
            continue
        ev_id, dt, ve = m.group(1), m.group(2), m.group(3)
        try:
            d = datetime.date(2000 + int(dt[:2]), int(dt[2:4]), int(dt[4:6]))
        except ValueError:
            continue
        if d < today:
            continue
        title = name_el.get_text(" ", strip=True)
        # titles often end with "at Moonshine Beach/Flats" — trim it
        title = re.sub(r"\s+at\s+Moonshine\s+(Beach|Flats)\s*$", "", title, flags=re.I)
        if not title:
            continue

        key = (ve, ev_id, d.isoformat())
        if key in seen:
            continue
        seen.add(key)

        venue, category = _VENUES[ve]
        events[ve].append({
            "id": "%s-%s-%s" % (category, d.isoformat(), ev_id),
            "title": title,
            "date": d.isoformat(),
            "time": "19:00",
            "venue": venue,
            "category": category,
            "price": "",
            "description": "",
            "url": a["href"],
        })
    return events


def scrape_beach(today=None):
    return _fetch_all(today or datetime.date.today())["beach"]


def scrape_flats(today=None):
    return _fetch_all(today or datetime.date.today())["flats"]


if __name__ == "__main__":
    all_ev = _fetch_all(datetime.date.today())
    for ve, evs in all_ev.items():
        print("Moonshine %s: %d events" % (ve, len(evs)))
        for e in evs[:5]:
            print("  ", e["date"], "-", e["title"])
