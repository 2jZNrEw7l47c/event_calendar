"""Scrape the McGuffie's Live schedule from https://mcguffieslive.com/shows

The site is GoDaddy Website Builder. There's no ticketing platform or events
API, but the schedule is laid out with GoDaddy's "Menu" widget, so each show is
a menu item with stable `data-aid` attributes:

    MENU_SECTION<n>_ITEM<m>_TITLE  ->  "July 16th at 8pm"   (date + time)
    MENU_SECTION<n>_ITEM<m>_PRICE  ->  "$12 COVER" / "NO COVER"
    MENU_SECTION<n>_ITEM<m>_DESC   ->  act name + genre (one or more <p> lines)

The data is present in the raw HTML (a plain GET works — no headless browser
needed). The TITLE times are hand-typed and loose, so we keep the original
listing text in the description and use a best-effort parsed time for ordering.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://mcguffieslive.com/shows"

_ITEM_FIELD = re.compile(r"(MENU_SECTION\d+_ITEM\d+)_(TITLE|PRICE|DESC)$")


def _paragraphs(el):
    if el is None:
        return []
    ps = [p.get_text(" ", strip=True) for p in el.select("p")]
    ps = [p for p in ps if p]
    if ps:
        return ps
    t = el.get_text(" ", strip=True)
    return [t] if t else []


def scrape(today=None, html=None):
    today = today or datetime.date.today()
    if html is None:
        resp = requests.get(URL, headers=common.UA, timeout=30)
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")

    # Group the flat data-aid elements back into items.
    items = {}
    for el in soup.select("[data-aid]"):
        m = _ITEM_FIELD.match(el.get("data-aid") or "")
        if m:
            items.setdefault(m.group(1), {})[m.group(2)] = el

    events = []
    for key, fields in items.items():
        title_text = fields["TITLE"].get_text(" ", strip=True) if "TITLE" in fields else ""
        m = re.match(r"([A-Za-z]+)\s+(\d{1,2})", title_text)   # "July 16th ..."
        if not m:
            continue
        month = common.month_to_num(m.group(1))
        if not month:
            continue
        d = common.infer_date(month, int(m.group(2)), today)
        if not d:
            continue

        time_part = ""
        tm = re.search(r"\bat\s+(.+)$", title_text)
        if tm:
            time_part = tm.group(1).strip()
        clock = common.parse_loose_time(time_part) or "20:00"

        desc_lines = _paragraphs(fields.get("DESC"))
        act = desc_lines[0] if desc_lines else title_text
        rest = desc_lines[1:]

        # Preserve the venue's own wording (times, hosts, notes) so nothing the
        # loose parser dropped is lost to the reader.
        desc_bits = rest + ["As listed: " + title_text]
        description = " · ".join(b for b in desc_bits if b)

        price = fields["PRICE"].get_text(" ", strip=True) if "PRICE" in fields else ""

        events.append({
            "id": "mcg-" + key.lower().replace("menu_section", "s").replace("_item", "i"),
            "title": act or "(see listing)",
            "date": d.isoformat(),
            "time": clock,
            "venue": "McGuffie's Live",
            "category": "mcguffies",
            "price": price,
            "description": description,
            "url": None,
        })

    return events


if __name__ == "__main__":
    evs = scrape()
    print("McGuffie's: %d events" % len(evs))
    for e in sorted(evs, key=lambda x: (x["date"], x["time"]))[:8]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
