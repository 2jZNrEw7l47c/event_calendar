"""Worldbeat Cultural Center, Balboa Park — WordPress + The Events Calendar (Tribe REST API)."""

import tribe_events

BASE = "https://www.worldbeatcenter.org"


def scrape(today=None):
    return tribe_events.scrape_tribe(BASE, "Worldbeat Center", "worldbeat", today)


if __name__ == "__main__":
    evs = scrape()
    print("Worldbeat Center: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
