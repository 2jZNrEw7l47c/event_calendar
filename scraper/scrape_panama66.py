"""Panama 66 (panama66.com/livemusic) — Squarespace day-list (see sqsp_daylist)."""
import sqsp_daylist


def scrape(today=None):
    return sqsp_daylist.scrape_daylist(
        "https://www.panama66.com/livemusic", "Panama 66", "panama66", today)


if __name__ == "__main__":
    evs = scrape()
    print("Panama 66: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
