"""SPIN nightclub (spinnightclub.com) — Eventbrite ticketing (see
eventbrite_events). Note: much of SPIN's programming is DJ-driven, so many
events will be dropped by the site-wide DJ keyword filter."""
import eventbrite_events


def scrape(today=None):
    return eventbrite_events.scrape_eventbrite(
        "https://spinnightclub.com", "SPIN", "spin", today)


if __name__ == "__main__":
    evs = scrape()
    print("SPIN: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
