"""Spreckels Organ Pavilion, Balboa Park — recurring events.

The Spreckels Organ Society's Squarespace site doesn't publish a machine-
readable schedule, but its signature program is fixed: free civic organ
concerts every Sunday at 2 PM, running since 1917 (see /sundays). We expand
that as a recurring rule, like Camel's Bar and Queen Bee's.

The Summer International Organ Festival (Monday evenings in summer) is NOT
generated because its dates/artists vary — check spreckelsorgan.org for it.
"""

import datetime

SUNDAY = 6
HORIZON_MONTHS = 6


def _add_months(d, months):
    m = d.month - 1 + months
    return datetime.date(d.year + m // 12, m % 12 + 1, 1)


def scrape(today=None):
    today = today or datetime.date.today()
    start = datetime.date(today.year, today.month, 1)
    end = _add_months(start, HORIZON_MONTHS)

    events = []
    d = start
    one = datetime.timedelta(days=1)
    while d < end:
        if d.weekday() == SUNDAY:
            events.append({
                "id": "spreckels-%s-sunday-concert" % d.isoformat(),
                "title": "Sunday Organ Concert",
                "date": d.isoformat(),
                "time": "14:00",
                "venue": "Spreckels Organ Pavilion",
                "category": "spreckels",
                "price": "Free",
                "description": "Weekly civic organ concert at the Spreckels Organ Pavilion, Balboa Park. Every Sunday, 2 PM, free — a tradition since 1917.",
                "url": "https://spreckelsorgan.org/sundays",
            })
        d += one
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Spreckels: %d occurrences" % len(evs))
    for e in evs[:5]:
        print("  ", e["date"], e["time"], "-", e["title"])
