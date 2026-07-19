"""Blind Lady Ale House (blindladyalehouse.com) — same Squarespace day-list
format as Panama 66 (same operators; see sqsp_daylist)."""
import sqsp_daylist


def scrape(today=None):
    return sqsp_daylist.scrape_daylist(
        "https://www.blindladyalehouse.com", "Blind Lady Ale House", "blindlady", today)


if __name__ == "__main__":
    evs = scrape()
    print("Blind Lady: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
