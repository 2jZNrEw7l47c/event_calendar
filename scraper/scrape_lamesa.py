"""La Mesa Village Association (lamesavillageassociation.org) — event calendar.

DotNetNuke site with a Telerik RadScheduler month grid, server-rendered: each
td has <a class="rsDateHeader" title="7/24/2026"> (a full date!) and one
.rsApt block per event with the name in its title attribute.

Titles are generic ("Car Show", "Farmers Market"), so per site policy every
event is prefixed "La Mesa Village - ".
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.lamesavillageassociation.org/la-mesa-village-calendar-of-events"

PREFIX = "La Mesa Village - "


def _default_time(title):
    t = title.lower()
    if "six" in t or "concert" in t:
        return "18:00"
    if "movie" in t:
        return "19:00"
    if "farmers market" in t:
        return "15:00"
    return "17:00"


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=35)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for cell in soup.find_all("td"):
        header = cell.select_one("a.rsDateHeader[title]")
        if not header:
            continue
        m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", header["title"])
        if not m:
            continue
        try:
            d = datetime.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError:
            continue
        if d < today:
            continue

        for apt in cell.select(".rsApt[title]"):
            name = apt["title"].strip()
            if not name:
                continue
            title = PREFIX + name
            key = (d.isoformat(), name.lower())
            if key in seen:
                continue
            seen.add(key)
            events.append({
                "id": "lamesa-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", name.lower())[:30]),
                "title": title,
                "date": d.isoformat(),
                "time": _default_time(name),
                "venue": "La Mesa Village",
                "category": "lamesa",
                "price": "",
                "description": "",
                "url": URL,
            })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("La Mesa Village: %d events" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], e["time"], "-", e["title"])
