"""Banshee Bar (thebansheebar.com) — GoDaddy site embedding a DICE event-list
widget. Events come from DICE's partner API (see dice_events.py).

The api key + promoter below are the widget's own public config, read from the
embed on the events page. If the schedule ever stops updating, re-check that
config on https://thebansheebar.com/events.
"""

import dice_events

API_KEY = "j24INW1UW9c097FLX_sqS1BCqF-vnAvOqQHNBzPoWcCp4pTc"
PROMOTER = "LSD & AD BAR ADVENTURES LLC"


def scrape(today=None):
    return dice_events.scrape_dice(API_KEY, PROMOTER, "Banshee Bar", "banshee", today)


if __name__ == "__main__":
    evs = scrape()
    print("Banshee Bar: %d events" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
