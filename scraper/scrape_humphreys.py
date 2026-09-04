"""Humphrey's Concerts by the Bay — humphreysconcerts.com/schedule.cfm.

Used to be pulled from the shared casbahmusic.com feed (see scrape_casbah),
on the assumption Casbah Presents still books this room. That's no longer
true: casbahmusic.com has dropped Humphrey's entirely — no /venues/ page, no
mention in its nav, and its own WordPress search index returns zero hits for
"humphrey" — while the venue's own site is actively selling a full concert
season. So we fetch straight from the source instead.

Each show is a server-rendered "Add to Calendar" widget
(`<div class="addeventatc">`) with plain `.start` / `.title` spans (no JS
needed); its sibling `.performance-title a` carries the Ticketmaster buy link
plus a `data-tprice` status ("AVAILABLE" or the literal "Sold Out" — the page
never prints a dollar price, just availability).
"""

import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.humphreysconcerts.com/schedule.cfm"


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=40)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    for row in soup.select(".row.padding-5.sched-separator-line"):
        widget = row.select_one(".addeventatc")
        if not widget:
            continue  # past-season rows with no calendar widget

        start_el = widget.select_one(".start")
        title_el = widget.select_one(".title")
        if not start_el or not title_el:
            continue
        try:
            dt = datetime.datetime.strptime(
                start_el.get_text(strip=True), "%m/%d/%Y %I:%M %p")
        except ValueError:
            continue
        if dt.date() < today:
            continue

        title = title_el.get_text(" ", strip=True)
        if not title:
            continue

        link = row.select_one(".performance-title a")
        status = (link.get("data-tprice") or "").strip().lower() if link else ""
        if status == "sold out":
            continue
        url = (link.get("data-buytixlink") or None) if link else None
        pid = (link.get("data-pid") or None) if link else None

        events.append({
            "id": "humphreys-" + (pid or (dt.date().isoformat() + dt.strftime("%H%M"))),
            "title": title,
            "date": dt.date().isoformat(),
            "time": dt.strftime("%H:%M"),
            "venue": "Humphrey's Concerts",
            "category": "humphreys",
            "price": "",
            "description": "",
            "url": url,
        })

    return events


if __name__ == "__main__":
    evs = scrape()
    print("Humphrey's Concerts: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
