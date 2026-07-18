"""Belly Up (bellyup.com) — WordPress + TicketWeb plugin."""
import ticketweb_events

URL = "https://bellyup.com/shows/"


def scrape(today=None):
    return ticketweb_events.scrape_ticketweb(URL, "Belly Up", "bellyup", today)


if __name__ == "__main__":
    evs = scrape()
    print("Belly Up: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
