"""Camel's Bar (camelsbarandgrill.com) — recurring events.

Camel's has no real online schedule, just a pasted text description of its
standing weekly/monthly jams. So this module isn't a scraper: it expands those
recurrence rules into concrete dated occurrences (a rolling window from the
start of the current month, HORIZON_MONTHS ahead) so they populate the list and
calendar like any other event.

Source text (as provided):
    Blue's Berry Jam hosted by John Frazier
    Every Tuesday 7PM-10PM

    Blues Jam with John January
    Every 2nd Sunday 1pm

Update the RULES below if the venue changes its standing schedule.
"""

import datetime

# Monday=0 ... Sunday=6
TUESDAY, SUNDAY = 1, 6

HORIZON_MONTHS = 6   # how far ahead to generate occurrences

RULES = [
    {
        "slug": "blues-berry-jam",
        "title": "Blue's Berry Jam",
        "time": "19:00",
        "freq": "weekly",
        "weekday": TUESDAY,
        "description": "Weekly blues jam hosted by John Frazier. Every Tuesday, 7–10PM.",
    },
    {
        "slug": "blues-jam-john-january",
        "title": "Blues Jam with John January",
        "time": "13:00",
        "freq": "monthly_nth",
        "weekday": SUNDAY,
        "nth": 2,
        "description": "Blues jam hosted by John January. Every 2nd Sunday, 1PM.",
    },
]


def _add_months(d, months):
    m = d.month - 1 + months
    year = d.year + m // 12
    month = m % 12 + 1
    return datetime.date(year, month, 1)


def _matches(rule, d):
    if rule["freq"] == "weekly":
        return d.weekday() == rule["weekday"]
    if rule["freq"] == "monthly_nth":
        # nth occurrence of the weekday within the month
        return d.weekday() == rule["weekday"] and (d.day - 1) // 7 == rule["nth"] - 1
    return False


def scrape(today=None):
    today = today or datetime.date.today()
    start = datetime.date(today.year, today.month, 1)
    end = _add_months(start, HORIZON_MONTHS)

    events = []
    d = start
    one_day = datetime.timedelta(days=1)
    while d < end:
        for rule in RULES:
            if _matches(rule, d):
                events.append({
                    "id": "camels-%s-%s" % (d.isoformat(), rule["slug"]),
                    "title": rule["title"],
                    "date": d.isoformat(),
                    "time": rule["time"],
                    "venue": "Camel's Bar",
                    "category": "camels",
                    "price": "",
                    "description": rule["description"],
                    "url": None,
                })
        d += one_day
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Camel's Bar: %d occurrences generated" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], e["time"], "-", e["title"])
