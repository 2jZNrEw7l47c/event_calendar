"""Whistle Stop (whistlestopbar.com) — WordPress + The Events Calendar."""
import tribe_events

BASE = "https://www.whistlestopbar.com"


def scrape(today=None):
    return tribe_events.scrape_tribe(BASE, "Whistle Stop", "whistlestop", today)


if __name__ == "__main__":
    evs = scrape()
    print("Whistle Stop: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
