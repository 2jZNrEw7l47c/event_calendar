"""Soda Bar (sodabarmusic.com) — WordPress site embedding a DICE event-list
widget. Events come from DICE's partner API (see dice_events.py).

The api key + promoter below are the widget's own public config, read from the
embed on the homepage. If the schedule stops updating, re-check that config in
the DiceEventListWidget.create({...}) call on https://sodabarmusic.com.
"""

import dice_events

API_KEY = "7eKoPj5BJI5D83snVEQ9S5uHj4SO9j07aw5qh3VR"
PROMOTER = "Big Soda LLC DBA Soda Bar"


def scrape(today=None):
    return dice_events.scrape_dice(API_KEY, PROMOTER, "Soda Bar", "sodabar", today)


if __name__ == "__main__":
    evs = scrape()
    print("Soda Bar: %d events" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], e["time"], "-", e["title"], "|", e["price"])
