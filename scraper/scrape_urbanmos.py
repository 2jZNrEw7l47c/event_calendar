"""Urban MO's Bar & Grill, Hillcrest (urbanmos.com) — The Events Calendar API.

Note: the original listing had mosuniverse.com ("Mo's"), which now redirects
here. Their calendar is dense with recurring nightly programming (drag shows,
karaoke, bingo...), so expect a large count; the shared tribe helper's
120-day horizon and (date, title) dedupe keep it manageable.
"""
import tribe_events

URL = "https://urbanmos.com"


def scrape(today=None):
    return tribe_events.scrape_tribe(URL, "Urban MO's", "urbanmos", today)


if __name__ == "__main__":
    evs = scrape()
    print("Urban MO's: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
