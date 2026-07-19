"""Scrape the Casbah schedule from https://www.casbahmusic.com

The site is WordPress + the See Tickets plugin, which renders every event into
the page HTML server-side (a plain GET returns fully-populated markup — no JS
execution needed). Each event is a `.seetickets-list-event-container` block with
semantic sub-classes.

The homepage is the hub for the whole "Casbah Presents" family, so the same
feed also lists shows at rooms we don't scrape anywhere else — Lou Lou's
Jungle Room, Humphrey's Concerts by the Bay, Quartyard. `scrape_for_venue`
extracts any one venue from the shared page (fetched once per build via a
module-level cache); the thin scrape_loulous / scrape_humphreys /
scrape_quartyard modules reuse it. Rooms with their own scrapers (Belly Up,
Soda Bar, ...) are ignored here.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.casbahmusic.com"

# One shared fetch per build (keyed by date so long-lived processes refetch).
_cache = {"day": None, "html": None}


def _get_html():
    today = datetime.date.today()
    if _cache["day"] != today:
        resp = requests.get(URL, headers=common.UA, timeout=30)
        resp.raise_for_status()
        _cache.update(day=today, html=resp.text)
    return _cache["html"]


def _text(node, selector):
    el = node.select_one(selector)
    return el.get_text(" ", strip=True) if el else ""


def scrape_for_venue(venue_match, venue_name, category, today=None, html=None):
    """Extract one venue's shows from the shared Casbah Presents feed.

    venue_match: lowercase substring matched against the card's `.venue` text
    (e.g. "at casbah" matches exactly; "lou lou" matches the longer label).
    """
    today = today or datetime.date.today()
    if html is None:
        html = _get_html()

    soup = BeautifulSoup(html, "html.parser")
    events = []

    for card in soup.select(".seetickets-list-event-container"):
        venue = _text(card, ".venue").strip().lower()
        if venue_match not in venue:
            continue

        # Drop sold-out / cancelled shows (See Tickets marks the buy button).
        btn = card.select_one("a.seetickets-buy-btn")
        btn_cls = " ".join(btn.get("class", [])) if btn else ""
        if "button-soldout" in btn_cls or "button-cancelled" in btn_cls:
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
            "id": category + "-" + (event_id or (d.isoformat() + (clock or ""))),
            "title": title,
            "date": d.isoformat(),
            "time": clock or "20:00",
            "venue": venue_name,
            "category": category,
            "price": _text(card, ".price"),
            "description": description,
            "url": url,
        })

    return events


def scrape(today=None, html=None):
    # "at casbah" is the exact label for the Casbah room; substring match is
    # safe because no other family venue contains the word "casbah".
    return scrape_for_venue("at casbah", "Casbah", "casbah", today, html)


if __name__ == "__main__":
    evs = scrape()
    print("Casbah: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
