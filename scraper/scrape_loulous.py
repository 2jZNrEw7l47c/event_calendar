"""Lou Lou's Jungle Room @ the Lafayette Hotel — booked by Casbah Presents;
events come from casbahmusic.com (see scrape_casbah). Unlike Quartyard/Casbah,
Lou Lou's shows are unreliable on the homepage's event widget — it's a
curated subset that often drops this room's cards entirely — so we pull from
the venue's own casbahmusic.com page instead, where its shows are appended
after the same generic list.
"""

import scrape_casbah

URL = "https://www.casbahmusic.com/venues/lou-lous/"


def scrape(today=None):
    return scrape_casbah.scrape_for_venue(
        "lou lou", "Lou Lou's Jungle Room", "loulous", today, page_url=URL)


if __name__ == "__main__":
    evs = scrape()
    print("Lou Lou's Jungle Room: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
