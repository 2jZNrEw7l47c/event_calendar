"""California Center for the Arts, Escondido — WordPress + The Events Calendar (Tribe REST API)."""

import tribe_events

BASE = "https://artcenter.org"


def scrape(today=None):
    return tribe_events.scrape_tribe(BASE, "CCA Escondido", "ccae", today)


if __name__ == "__main__":
    evs = scrape()
    print("CCA Escondido: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
