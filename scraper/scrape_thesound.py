"""The Sound (thesoundsd.com) — WordPress + TicketWeb plugin."""
import ticketweb_events

URL = "https://thesoundsd.com/"


def scrape(today=None):
    return ticketweb_events.scrape_ticketweb(URL, "The Sound", "thesound", today)


if __name__ == "__main__":
    evs = scrape()
    print("The Sound: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
