"""Generic schema.org JSON-LD event extractor.

Many venue sites embed their schedule as <script type="application/ld+json">
Event / MusicEvent objects (name, startDate, location, offers, url). This module
pulls those out and normalizes them, so a per-venue scraper can often be a thin
wrapper around extract_ld_events().
"""

import re
import json
import html
import datetime

import requests

import common

EVENT_TYPES = {"Event", "MusicEvent", "TheaterEvent", "ComedyEvent",
               "DanceEvent", "Festival", "SportsEvent", "SocialEvent"}


def _iter_ld_blocks(html):
    for m in re.finditer(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html, re.S | re.I):
        raw = m.group(1).strip()
        if not raw:
            continue
        try:
            yield json.loads(raw)
        except Exception:
            # Some sites concatenate multiple objects or have trailing commas;
            # try to salvage the first valid JSON value.
            try:
                yield json.loads(raw[:raw.rfind("}") + 1])
            except Exception:
                continue


def _walk(node, out):
    """Collect every dict that looks like a schema.org event."""
    if isinstance(node, list):
        for x in node:
            _walk(x, out)
    elif isinstance(node, dict):
        t = node.get("@type")
        types = set(t if isinstance(t, list) else [t]) if t else set()
        if types & EVENT_TYPES:
            out.append(node)
        for key in ("@graph", "itemListElement", "item", "subEvent", "events"):
            if key in node:
                _walk(node[key], out)


def _price(offers):
    if not offers:
        return ""
    if isinstance(offers, dict):
        offers = [offers]
    prices = []
    for o in offers:
        if not isinstance(o, dict):
            continue
        p = o.get("price") or o.get("lowPrice")
        if p not in (None, "", "0", 0):
            cur = o.get("priceCurrency", "")
            sym = "$" if cur in ("USD", "", None) else cur + " "
            prices.append(sym + str(p))
    return prices[0] if prices else ""


def _location_name(loc):
    if isinstance(loc, list):
        loc = loc[0] if loc else None
    if isinstance(loc, dict):
        return loc.get("name", "") or ""
    if isinstance(loc, str):
        return loc
    return ""


def parse_start(dt):
    """schema.org startDate is ISO-8601 -> (date str, 'HH:MM' or None)."""
    if not dt or not isinstance(dt, str):
        return None, None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?", dt)
    if not m:
        return None, None
    d = "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
    tm = None
    if m.group(4):
        tm = "%s:%s" % (m.group(4), m.group(5))
    return d, tm


def extract_ld_events(html):
    """Return a list of raw schema.org event dicts found in the page."""
    found = []
    for block in _iter_ld_blocks(html):
        _walk(block, found)
    # de-dupe by (name, startDate)
    seen = set()
    uniq = []
    for e in found:
        key = (str(e.get("name")), str(e.get("startDate")))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(e)
    return uniq


def scrape_ld(url, venue, category, today=None, upcoming_only=True):
    """Fetch a page and return normalized events from its JSON-LD."""
    today = today or datetime.date.today()
    resp = requests.get(url, headers=common.UA, timeout=30)
    resp.raise_for_status()
    page = common.decode(resp)
    events = []
    for e in extract_ld_events(page):
        name = e.get("name")
        if not name:
            continue
        name = html.unescape(name).replace("�", "").strip()
        d, tm = parse_start(e.get("startDate"))
        if not d:
            continue
        if upcoming_only and d < today.isoformat():
            continue
        events.append({
            "id": "%s-%s-%s" % (category, d, re.sub(r"[^a-z0-9]+", "-", name.lower())[:40]),
            "title": name.strip(),
            "date": d,
            "time": tm or "20:00",
            "venue": venue,
            "category": category,
            "price": _price(e.get("offers")),
            "description": _location_name(e.get("location")),
            "url": e.get("url") or url,
        })
    return events


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.houseofblues.com/sandiego"
    evs = scrape_ld(url, "Test", "test")
    print("%d events from %s" % (len(evs), url))
    for e in evs[:12]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
