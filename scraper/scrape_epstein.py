"""Epstein Family Amphitheater, UC San Diego — WordPress + The Events Calendar (Tribe REST API)."""

import tribe_events

BASE = "https://amphitheater.ucsd.edu"


def scrape(today=None):
    return tribe_events.scrape_tribe(BASE, "Epstein Amphitheater", "epstein", today)


if __name__ == "__main__":
    evs = scrape()
    print("Epstein Amphitheater: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
