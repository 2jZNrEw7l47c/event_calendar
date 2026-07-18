"""The Observatory North Park (observatorysd.com) — schema.org JSON-LD."""
import ld_events

URL = "https://www.observatorysd.com"


def scrape(today=None):
    return ld_events.scrape_ld(URL, "Observatory North Park", "observatory", today)


if __name__ == "__main__":
    evs = scrape()
    print("Observatory North Park: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
