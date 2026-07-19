"""710 Beach Club, Pacific Beach (710bc.com) — Eventbrite ticketing (see
eventbrite_events)."""
import eventbrite_events


def scrape(today=None):
    return eventbrite_events.scrape_eventbrite(
        "https://www.710bc.com/events", "710 Beach Club", "beach710", today)


if __name__ == "__main__":
    evs = scrape()
    print("710 Beach Club: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
