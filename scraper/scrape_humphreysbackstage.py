"""Humphrey's Backstage Live (the lounge, distinct from the Concerts by the Bay stage) — WordPress + The Events Calendar (Tribe REST API)."""

import tribe_events

BASE = "https://www.humphreysbackstagelive.com"


def scrape(today=None):
    return tribe_events.scrape_tribe(BASE, "Humphrey's Backstage", "humpbackstage", today)


if __name__ == "__main__":
    evs = scrape()
    print("Humphrey's Backstage: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
