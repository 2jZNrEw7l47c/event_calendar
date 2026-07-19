"""Run every venue scraper, combine the results, and write the data file the
events page loads (js/events-data.js), plus a raw data/events.json for reference.

Usage:
    python scraper/build_events_data.py

Each scraper exposes scrape(today) -> list[event dict]. Adding a venue is just
importing its module and appending it to SCRAPERS below.
"""

import os
import re
import json
import datetime

import scrape_casbah
import scrape_mcguffies
import scrape_camels
import scrape_deanos
import scrape_whistlestop
import scrape_holdingco
import scrape_houseofblues
import scrape_observatory
import scrape_bellyup
import scrape_brick
import scrape_thesound
import scrape_kensington
import scrape_banshee
import scrape_sodabar
import scrape_soma
import scrape_winstons
import scrape_musicbox
import scrape_towerbar
import scrape_queenbees
import scrape_blackcat
import scrape_loulous
import scrape_humphreys
import scrape_quartyard
import scrape_ccae
import scrape_humphreysbackstage
import scrape_newvillage
import scrape_pechanga
import scrape_worldbeat
import scrape_epstein

# (category key, human label, module). Order controls filter-pill order.
SCRAPERS = [
    ("casbah", "Casbah", scrape_casbah),
    ("mcguffies", "McGuffie's Live", scrape_mcguffies),
    ("camels", "Camel's Bar", scrape_camels),
    ("whistlestop", "Whistle Stop", scrape_whistlestop),
    ("holdingco", "The Holding Company", scrape_holdingco),
    ("houseofblues", "House of Blues", scrape_houseofblues),
    ("observatory", "Observatory North Park", scrape_observatory),
    ("bellyup", "Belly Up", scrape_bellyup),
    ("brick", "Brick By Brick", scrape_brick),
    ("thesound", "The Sound", scrape_thesound),
    ("kensington", "The Kensington Club", scrape_kensington),
    ("banshee", "Banshee Bar", scrape_banshee),
    ("sodabar", "Soda Bar", scrape_sodabar),
    ("soma", "SOMA", scrape_soma),
    ("winstons", "Winston's", scrape_winstons),
    ("musicbox", "Music Box", scrape_musicbox),
    ("towerbar", "Tower Bar", scrape_towerbar),
    ("queenbees", "Queen Bee's", scrape_queenbees),
    # Secondary venues — shared Casbah Presents feed (one fetch, three venues)
    ("loulous", "Lou Lou's Jungle Room", scrape_loulous),
    ("humphreys", "Humphrey's Concerts", scrape_humphreys),
    ("quartyard", "Quartyard", scrape_quartyard),
    # Secondary venues — Tribe (The Events Calendar) REST API
    ("ccae", "CCA Escondido", scrape_ccae),
    ("humpbackstage", "Humphrey's Backstage", scrape_humphreysbackstage),
    ("newvillage", "New Village Arts", scrape_newvillage),
    ("pechanga", "Pechanga Arena", scrape_pechanga),
    ("worldbeat", "Worldbeat Center", scrape_worldbeat),
    ("epstein", "Epstein Amphitheater", scrape_epstein),
]

# Belly Up's feed aggregates other rooms (incl. The Sound). When the same show
# (same title + date) appears for both, keep The Sound's copy and drop Belly Up's.
DEDUP_PREFER = [("thesound", "bellyup")]

# Drop any event whose title or description matches one of these (whole-word,
# case-insensitive). Keeps happy hours and metal nights out of the listings.
EXCLUDE_KEYWORDS = [r"happy hour", r"metal", r"djs?"]
_EXCLUDE_RE = re.compile(r"\b(?:%s)\b" % "|".join(EXCLUDE_KEYWORDS), re.I)

# Image-only venues: no structured events, just a flyer we show in a dialog.
# (label, module) — each module.scrape(today) returns flyer metadata or None.
FLYER_SCRAPERS = [
    ("Deano's Pub", scrape_deanos),
    ("Black Cat Bar", scrape_blackcat),
]

# Link-out venues: large arenas we don't scrape (Ticketmaster/Live Nation
# anti-bot). Instead we surface a pill that links straight to their ticketing
# page. Shown in the special-case row next to the flyer button(s).
LINKOUTS = [
    {"venue": "Snapdragon Stadium",
     "url": "https://www.ticketmaster.com/snapdragon-stadium-tickets-san-diego/venue/82847"},
    {"venue": "North Island Amphitheatre",
     "url": "https://www.livenation.com/venue/KovZpa2WZe/north-island-credit-union-amphitheatre-events"},
    {"venue": "Petco Park",
     "url": "https://www.ticketmaster.com/petco-park-tickets-san-diego/venue/82561"},
]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS_OUT = os.path.join(ROOT, "js", "events-data.js")
JSON_OUT = os.path.join(ROOT, "data", "events.json")


def _excluded(event):
    return bool(_EXCLUDE_RE.search(event.get("title", "")) or
                _EXCLUDE_RE.search(event.get("description", "")))


def _norm(title):
    return re.sub(r"[^a-z0-9]+", "", title.lower())


def _dedup_across_venues(events, per_venue):
    """Drop cross-listed duplicates per DEDUP_PREFER (keep first venue, drop second)."""
    for keep_cat, drop_cat in DEDUP_PREFER:
        keep_keys = {(e["date"], _norm(e["title"])) for e in events if e["category"] == keep_cat}
        if not keep_keys:
            continue
        kept = []
        removed = 0
        for e in events:
            if e["category"] == drop_cat and (e["date"], _norm(e["title"])) in keep_keys:
                removed += 1
                continue
            kept.append(e)
        events = kept
        if removed:
            print("  (deduped %d %s events also listed by %s)" % (removed, drop_cat, keep_cat))
    return events


def _identity(e):
    """Stable cross-build identity for an event. Some scraper ids embed
    volatile bits (e.g. DICE checksums), so compare on venue+date+title."""
    return "%s|%s|%s" % (e["category"], e["date"], _norm(e["title"]))


def _stamp_added(events, today):
    """Mark each event with the build date it was first seen ("added").

    Compares against the previous data/events.json: events already known keep
    their original stamp; genuinely new ones get today's date. The page uses
    the newest batch of stamps to show "what's new since the last scrape".
    Returns the number of newly added events this run.
    """
    prev = None
    try:
        with open(JSON_OUT, encoding="utf-8") as f:
            prev = {_identity(e): e.get("added")
                    for e in json.load(f).get("events", [])}
    except (OSError, ValueError):
        pass

    today_str = today.isoformat()
    new_count = 0
    for e in events:
        if prev is None:
            # First build with tracking: no baseline, so nothing is "new".
            e["added"] = None
        elif _identity(e) in prev:
            e["added"] = prev[_identity(e)]
        else:
            e["added"] = today_str
            new_count += 1
    return new_count


def main():
    today = datetime.date.today()
    all_events = []
    categories = {}
    per_venue = {}

    excluded = 0
    for key, label, module in SCRAPERS:
        try:
            evs = module.scrape(today)
        except Exception as exc:                       # keep other venues if one fails
            print("!! %s failed: %s" % (label, exc))
            evs = []
        kept = [e for e in evs if not _excluded(e)]
        excluded += len(evs) - len(kept)
        per_venue[label] = len(kept)
        if kept:
            categories[key] = label
            all_events.extend(kept)

    if excluded:
        print("  (filtered %d events matching %s)" % (excluded, "/".join(EXCLUDE_KEYWORDS)))

    all_events = _dedup_across_venues(all_events, per_venue)

    # Sort chronologically (date then time) — the page also sorts, but a tidy
    # file is easier to diff and eyeball.
    all_events.sort(key=lambda e: (e["date"], e["time"], e["title"].lower()))

    new_count = _stamp_added(all_events, today)
    if new_count:
        print("  (%d newly added events since last build)" % new_count)

    # Image-only venues: fetch each flyer.
    flyers = []
    for label, module in FLYER_SCRAPERS:
        try:
            info = module.scrape(today)
        except Exception as exc:
            print("!! %s flyer failed: %s" % (label, exc))
            info = None
        if info:
            info = dict(info, venue=label)
            flyers.append(info)

    payload_events = json.dumps(all_events, indent=2, ensure_ascii=False)
    payload_cats = json.dumps(categories, indent=2, ensure_ascii=False)
    payload_flyers = json.dumps(flyers, indent=2, ensure_ascii=False)
    payload_linkouts = json.dumps(LINKOUTS, indent=2, ensure_ascii=False)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    header = (
        "/* ------------------------------------------------------------------\n"
        "   AUTO-GENERATED by scraper/build_events_data.py — do not edit by hand.\n"
        "   Last built: %s\n"
        "   Sources: Casbah (casbahmusic.com), McGuffie's Live (mcguffieslive.com),\n"
        "            Camel's Bar (recurring events), Deano's Pub flyer (deanospub.com)\n"
        "   Exposes window.CATEGORIES, window.EVENTS, window.FLYERS, window.LINKOUTS.\n"
        "   ------------------------------------------------------------------ */\n\n"
    ) % stamp

    js = header + "window.CATEGORIES = " + payload_cats + ";\n\n" \
        + "window.EVENTS = " + payload_events + ";\n\n" \
        + "window.FLYERS = " + payload_flyers + ";\n\n" \
        + "window.LINKOUTS = " + payload_linkouts + ";\n"

    os.makedirs(os.path.dirname(JS_OUT), exist_ok=True)
    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
    with open(JS_OUT, "w", encoding="utf-8") as f:
        f.write(js)
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": stamp, "categories": categories,
                   "events": all_events, "flyers": flyers, "linkouts": LINKOUTS},
                  f, indent=2, ensure_ascii=False)

    print("Built %s" % os.path.relpath(JS_OUT, ROOT))
    for label, n in per_venue.items():
        print("  %-16s %3d events" % (label, n))
    print("  %-16s %3d events total" % ("=>", len(all_events)))
    for fl in flyers:
        print("  %-16s flyer -> %s" % (fl["venue"], fl.get("image") or fl["source"]))


if __name__ == "__main__":
    main()
