"""Balboa Park (balboapark.org) — The Events Calendar API.

Park-wide events feed (museums, gardens, performances, Marston Point, etc.).
Broader than a music venue, but the park hosts plenty of performances; the
venue label makes the source obvious so park events are easy to filter out
with the venue pills.
"""
import tribe_events

URL = "https://www.balboapark.org"


def scrape(today=None):
    return tribe_events.scrape_tribe(URL, "Balboa Park", "balboapark", today)


if __name__ == "__main__":
    evs = scrape()
    print("Balboa Park: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
