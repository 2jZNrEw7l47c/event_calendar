"""Scrape the Casbah schedule from https://www.casbahmusic.com

The site is WordPress + the See Tickets plugin, which renders every event into
the page HTML server-side (a plain GET returns fully-populated markup — no JS
execution needed). Each event is a `.seetickets-list-event-container` block with
semantic sub-classes.

The homepage is the hub for the whole "Casbah Presents" family (Belly Up, Soda
Bar, Whistle Stop, Observatory, ...), so we filter on the venue field to keep
only shows in the Casbah room itself.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.casbahmusic.com"
VENUE_LABEL = "at casbah"   # exact `.venue` text for the Casbah room


def _text(node, selector):
    el = node.select_one(selector)
    return el.get_text(" ", strip=True) if el else ""


def scrape(today=None, html=None):
    today = today or datetime.date.today()
    if html is None:
        resp = requests.get(URL, headers=common.UA, timeout=30)
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")
    events = []

    for card in soup.select(".seetickets-list-event-container"):
        venue = _text(card, ".venue")
        if venue.strip().lower() != VENUE_LABEL:
            continue

        date_text = _text(card, ".event-date")          # e.g. "Sun Jan 10"
        m = re.search(r"([A-Za-z]+)\s+(\d{1,2})", date_text)
        if not m:
            continue
        month = common.month_to_num(m.group(1))
        if not month:
            continue
        d = common.infer_date(month, int(m.group(2)), today)
        if not d:
            continue

        # Prefer show time; fall back to door time.
        clock = common.parse_clock(_text(card, ".see-showtime")) \
            or common.parse_clock(_text(card, ".see-doortime"))

        title = _text(card, ".headliners") or _text(card, ".event-header") or "(untitled)"

        link = card.select_one("a.seetickets-buy-btn") or card.select_one("a[href*='seetickets']")
        url = link["href"] if link and link.has_attr("href") else None
        event_id = None
        if url:
            mid = re.search(r"/(\d+)(?:\?|$)", url)
            event_id = mid.group(1) if mid else None

        desc_bits = [
            _text(card, ".event-header"),
            _text(card, ".genre"),
            _text(card, ".ages"),
        ]
        description = " · ".join(b for b in desc_bits if b)

        events.append({
            "id": "casbah-" + (event_id or (d.isoformat() + (clock or ""))),
            "title": title,
            "date": d.isoformat(),
            "time": clock or "20:00",
            "venue": "Casbah",
            "category": "casbah",
            "price": _text(card, ".price"),
            "description": description,
            "url": url,
        })

    return events


if __name__ == "__main__":
    evs = scrape()
    print("Casbah: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
