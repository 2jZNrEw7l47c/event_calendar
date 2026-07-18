"""House of Blues San Diego (houseofblues.com/sandiego) — schema.org JSON-LD."""
import ld_events

URL = "https://www.houseofblues.com/sandiego"


def scrape(today=None):
    evs = ld_events.scrape_ld(URL, "House of Blues", "houseofblues", today)
    # The HOB page lists the Voodoo Room shows too; keep them all under HOB.
    return evs


if __name__ == "__main__":
    evs = scrape()
    print("House of Blues: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
