"""The Heart OB, Ocean Beach (theheartob.com) — Wix Events.

The /event-calendar page embeds the Wix Events app state as JSON in the raw
HTML (titles, slugs, and scheduling with UTC start dates). No API call needed:
we scan windows around each event slug for its title and startDate, and
convert UTC to Pacific.
"""

import re
import datetime

import requests

import common

URL = "https://www.theheartob.com/event-calendar"

try:
    from zoneinfo import ZoneInfo
    _PACIFIC = ZoneInfo("America/Los_Angeles")
except Exception:                                     # pragma: no cover
    _PACIFIC = None

_SLUG = re.compile(r'"slug":"([a-z0-9\-]{6,60})"')
_TITLE = re.compile(r'"title":"([^"]{2,90})"')
_START = re.compile(r'"startDate":"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.\d+)?Z"')


def _pacific(iso):
    dt = datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S").replace(
        tzinfo=datetime.timezone.utc)
    if _PACIFIC is not None:
        loc = dt.astimezone(_PACIFIC)
    else:
        off = -7 if 3 <= dt.month <= 10 else -8
        loc = dt.astimezone(datetime.timezone(datetime.timedelta(hours=off)))
    return loc.date().isoformat(), "%02d:%02d" % (loc.hour, loc.minute)


def scrape(today=None):
    today = today or datetime.date.today()
    t = ""
    # Wix occasionally serves a non-hydrated page without the embedded events
    # JSON; a refetch almost always returns the full variant.
    for _ in range(3):
        resp = requests.get(URL, headers=common.UA, timeout=30)
        resp.raise_for_status()
        t = common.decode(resp)
        if _SLUG.search(t):
            break

    events = []
    seen = set()
    for m in _SLUG.finditer(t):
        slug = m.group(1)
        # In the Wix Events JSON, each event object lays out scheduling
        # (startDate), then title, then slug — so look *backwards* from the
        # slug for both, taking the nearest occurrence of each.
        window = t[max(0, m.start() - 4000):m.start()]
        titles = _TITLE.findall(window)
        starts = _START.findall(window)
        if not titles or not starts:
            continue
        title = titles[-1].replace("\\u0026", "&").strip()
        date, clock = _pacific(starts[-1])
        if date < today.isoformat():
            continue
        key = (date, title.lower())
        if key in seen:
            continue
        seen.add(key)
        events.append({
            "id": "heartob-%s-%s" % (date, slug[:30]),
            "title": title,
            "date": date,
            "time": clock,
            "venue": "The Heart OB",
            "category": "heartob",
            "price": "",
            "description": "",
            "url": "https://www.theheartob.com/event-details/" + slug,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Heart OB: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
