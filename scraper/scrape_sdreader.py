"""San Diego Reader events listing (sandiegoreader.com/events/) — aggregator.

The Reader's events page embeds schema.org JSON-LD for its picks. Each event's
real venue is in the LD location, which the shared helper keeps in the
description. Aggregator policy: build-level dedup drops any Reader event whose
(date, title) matches an event from an actual venue scraper.
"""
import ld_events

URL = "https://www.sandiegoreader.com/events/"


def scrape(today=None):
    return ld_events.scrape_ld(URL, "SD Reader picks", "sdreader", today)


if __name__ == "__main__":
    evs = scrape()
    print("SD Reader: %d events" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], e["time"], "-", e["title"], "@", e["description"][:30])
