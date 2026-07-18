"""Brick By Brick (brickbybrick.com) — WordPress + TicketWeb event-discovery plugin."""
import ticketweb_events

URL = "https://www.brickbybrick.com/"


def scrape(today=None):
    return ticketweb_events.scrape_ticketweb(URL, "Brick By Brick", "brick", today)


if __name__ == "__main__":
    evs = scrape()
    print("Brick By Brick: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
