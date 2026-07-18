"""One-off reconnaissance: probe each remaining primary venue's site to see what
platform/ticketing it uses and whether events are in the raw HTML. Not part of
the build; used to plan scrapers. Safe to delete."""

import re
import concurrent.futures as cf
import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}

VENUES = [
    ("Snapdragon Stadium", "https://snapdragonstadium.com"),
    ("The Holding Company", "https://www.theholdingcompanyob.com"),
    ("Ken Club", "https://www.kenclubsd.com"),
    ("Queen Bee's", "https://queenbeessd.com"),
    ("Black Cat Bar", "https://www.blackcatsd.com"),
    ("Brick By Brick", "https://www.brickbybrick.com"),
    ("Soda Bar", "https://www.sodabarmusic.com"),
    ("Music Box", "https://musicboxsd.com"),
    ("Banshee Bar", "https://www.bansheebar.com"),
    ("Belly Up", "https://bellyup.com"),
    ("North Island CU Amphitheatre", "https://www.livenation.com/venue/KovZpZAJ6nlA/north-island-credit-union-amphitheatre-events"),
    ("House of Blues", "https://www.houseofblues.com/sandiego"),
    ("Grand Ole BBQ", "https://grandolebbq.com"),
    ("The Jazz Lounge", "https://www.thejazzlounge.live"),
    ("Winston's", "https://winstonsob.com"),
    ("Tower Bar", "https://www.thetowerbar.com"),
    ("Observatory North Park", "https://www.observatorysd.com"),
    ("The Sound", "https://thesoundsd.com"),
    ("SOMA Sidestage", "https://www.somasandiego.com"),
    ("Whistle Stop", "https://www.whistlestopbar.com"),
    ("Petco Park", "https://www.mlb.com/padres/ballpark"),
]

PLATFORMS = ["seetickets", "ticketweb", "dice.fm", "eventbrite", "ticketmaster",
             "axs.com", "etix", "tixr", "prekindle", "venuepilot", "opendate",
             "songkick", "bandsintown", "squarespace", "wixstatic", "shopify"]

MARKERS = {
    "seetickets-list-event-container": "seetix-widget",
    "tribe-events": "the-events-calendar",
    "tribe_events": "the-events-calendar",
    "eventlist": "eventlist",
    "eventItem": "eventItem",
    "data-aid=\"MENU": "godaddy-menu",
    "application/ld+json": "jsonld",
}


def probe(item):
    name, url = item
    try:
        r = requests.get(url, headers=UA, timeout=25, allow_redirects=True)
        t = r.text
    except Exception as e:
        return name, url, "ERR: %s" % str(e)[:60], "", "", 0
    gen = ""
    g = re.search(r'name=["\']generator["\'] content=["\']([^"\']+)', t)
    if g:
        gen = g.group(1)[:28]
    plats = [p for p in PLATFORMS if p in t]
    # count ld+json event types
    ld_events = 0
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', t, re.S):
        if '"MusicEvent"' in m.group(1) or '"Event"' in m.group(1):
            ld_events += m.group(1).count('"@type"')
    marks = [v for k, v in MARKERS.items() if k in t]
    return name, url, gen, ",".join(plats), ",".join(sorted(set(marks))) + (" ld=%d" % ld_events if ld_events else ""), len(t)


def main():
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(probe, VENUES))
    print("%-26s %-26s %-24s %s" % ("VENUE", "GENERATOR", "TICKETING", "MARKERS"))
    print("-" * 110)
    for name, url, gen, plats, marks, ln in results:
        print("%-26s %-26s %-24s %s" % (name[:26], gen[:26], plats[:24], marks))


if __name__ == "__main__":
    main()
