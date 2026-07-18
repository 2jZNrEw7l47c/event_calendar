"""The Holding Company (theholdingcompanyob.com) — WordPress + The Events Calendar."""
import tribe_events

BASE = "https://www.theholdingcompanyob.com"


def scrape(today=None):
    return tribe_events.scrape_tribe(BASE, "The Holding Company", "holdingco", today)


if __name__ == "__main__":
    evs = scrape()
    print("The Holding Company: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
