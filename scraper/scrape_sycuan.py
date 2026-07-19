"""Sycuan Casino Resort (sycuan.com) — homepage event widget.

Server-rendered <div class="event-widget"> list: each item has
<span class="datetime">Thursday July 23, 2026 @ 8:00 PM</span> and
<span class="title">The River: Ingrid Andress: ...</span> where the title's
prefix names the room (The River / El Rio / Bull & Bourbon ...). We keep the
room in the description and the act as the title.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.sycuan.com"


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=40)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    # datetime/title spans aren't reliably wrapped in one container, so pair
    # each datetime with the next title span in document order.
    spans = soup.find_all("span", class_=["datetime", "title"])
    pairs = []
    pending = None
    for sp in spans:
        cls = " ".join(sp.get("class", []))
        if "mobile" in cls:        # duplicate numeric-format variant
            continue
        if "datetime" in cls:
            pending = sp
        elif "title" in cls and pending is not None:
            pairs.append((pending, sp))
            pending = None

    events = []
    seen = set()
    for dt, ti in pairs:
        text = dt.get_text(" ", strip=True)      # "Thursday July 23, 2026 @ 8:00 PM"
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
        clock = common.parse_clock(text) or "20:00"

        raw = ti.get_text(" ", strip=True)
        # Titles are usually "Room: Act: <date restated>" but sometimes just
        # "Act: <date>" — only treat the prefix as a room if we recognize it.
        rooms = ("the river", "el rio", "bull & bourbon", "lobby bar",
                 "retreat pool", "live & up close", "heritage")
        room, act = "", raw
        if ":" in raw:
            pre, rest = raw.split(":", 1)
            if pre.strip().lower() in rooms:
                room, act = pre, rest.strip()
        # strip a trailing restatement of the date/time from the act
        act = re.sub(r"[:,]?\s*\d{1,2}(:\d{2})?\s*[AP]M.*$", "", act, flags=re.I)
        act = re.sub(r"[:,]?\s*(Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day.*$", "", act, flags=re.I).strip(" :,-")
        if not act:
            continue

        key = (d.isoformat(), act.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "sycuan-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", act.lower())[:30]),
            "title": act,
            "date": d.isoformat(),
            "time": clock,
            "venue": "Sycuan Casino",
            "category": "sycuan",
            "price": "",
            "description": (room and room.strip() + " · " or "") + "Sycuan Casino Resort",
            "url": "https://www.sycuan.com/entertainment/",
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Sycuan: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["description"][:30])
