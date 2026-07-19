"""Humphrey's Concerts by the Bay — Casbah Presents lists its shows;
events come from the shared casbahmusic.com feed (see scrape_casbah), which is
fetched once per build. Only this venue's cards are extracted here.
"""

import scrape_casbah


def scrape(today=None):
    return scrape_casbah.scrape_for_venue("humphrey", "Humphrey's Concerts", "humphreys", today)


if __name__ == "__main__":
    evs = scrape()
    print("Humphrey's Concerts: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
