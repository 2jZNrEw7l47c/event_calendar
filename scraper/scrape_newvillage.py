"""New Village Arts theatre, Carlsbad — WordPress + The Events Calendar (Tribe REST API)."""

import tribe_events

BASE = "https://newvillagearts.org"


def scrape(today=None):
    return tribe_events.scrape_tribe(BASE, "New Village Arts", "newvillage", today)


if __name__ == "__main__":
    evs = scrape()
    print("New Village Arts: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
