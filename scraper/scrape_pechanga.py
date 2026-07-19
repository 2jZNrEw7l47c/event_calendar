"""Pechanga Arena San Diego — WordPress + The Events Calendar (Tribe REST API)."""

import tribe_events

BASE = "https://pechangaarenasd.com"


def scrape(today=None):
    return tribe_events.scrape_tribe(BASE, "Pechanga Arena", "pechanga", today)


if __name__ == "__main__":
    evs = scrape()
    print("Pechanga Arena: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
