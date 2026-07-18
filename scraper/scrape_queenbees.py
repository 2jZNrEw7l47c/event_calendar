"""Queen Bee's Art & Cultural Center (queenbeessd.com) — recurring events.

Their site is a Wix booking/landing site with no event feed; one-off shows are
promoted on social media only. What the site does state (on /classes) is the
standing weekly dance schedule, so — like Camel's Bar — we expand those
recurrence rules into dated occurrences.

Source text (from queenbeessd.com/classes, checked 2026-07):
    Salsa Sunday — every Sunday, 5:30 PM — $15 cover / $10 students
    Beginning Swing (Mercedes Moore) — every Tuesday, class 6:30 PM
    Beginner Line Dance Social — 1st & 3rd Wednesday, 7:00 PM — $15

Update RULES if the venue changes its standing schedule.
"""

import datetime

# Monday=0 ... Sunday=6
SUNDAY, TUESDAY, WEDNESDAY = 6, 1, 2

HORIZON_MONTHS = 6

RULES = [
    {
        "slug": "salsa-sunday",
        "title": "Salsa Sunday",
        "time": "17:30",
        "weekday": SUNDAY,
        "nths": None,                      # every week
        "price": "$15 / $10 students",
        "description": "Salsa & Bachata lessons with Positive Energy Dance Company, then social dancing. Every Sunday, 5:30 PM.",
    },
    {
        "slug": "beginning-swing",
        "title": "Beginning Swing with Mercedes Moore",
        "time": "18:30",
        "weekday": TUESDAY,
        "nths": None,
        "price": "$15 class + social / $10 social",
        "description": "All-levels swing class at 6:30 PM, social dancing from 7:30 PM. Every Tuesday.",
    },
    {
        "slug": "line-dance-social",
        "title": "Beginner Line Dance Social",
        "time": "19:00",
        "weekday": WEDNESDAY,
        "nths": (1, 3),                    # 1st & 3rd Wednesday
        "price": "$15",
        "description": "One-hour beginner line dance class and social. 1st & 3rd Wednesday, 7:00 PM.",
    },
]


def _add_months(d, months):
    m = d.month - 1 + months
    return datetime.date(d.year + m // 12, m % 12 + 1, 1)


def scrape(today=None):
    today = today or datetime.date.today()
    start = datetime.date(today.year, today.month, 1)
    end = _add_months(start, HORIZON_MONTHS)

    events = []
    d = start
    one_day = datetime.timedelta(days=1)
    while d < end:
        for rule in RULES:
            if d.weekday() != rule["weekday"]:
                continue
            if rule["nths"] and ((d.day - 1) // 7 + 1) not in rule["nths"]:
                continue
            events.append({
                "id": "qb-%s-%s" % (d.isoformat(), rule["slug"]),
                "title": rule["title"],
                "date": d.isoformat(),
                "time": rule["time"],
                "venue": "Queen Bee's",
                "category": "queenbees",
                "price": rule["price"],
                "description": rule["description"],
                "url": "https://www.queenbeessd.com/classes",
            })
        d += one_day
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Queen Bee's: %d occurrences" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
