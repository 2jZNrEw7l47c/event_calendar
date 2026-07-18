"""The Kensington Club / "Ken Club" (kensingtonclub1935.com) — Wix site.

The /calendar page lists shows as free text ("Friday, July 10th" followed by the
night's acts). Wix server-renders that text into the page HTML, so despite being
a JS-heavy site the schedule is present in a plain GET — no headless browser
needed.

We locate each "Weekday, Month Day" header and treat the text up to the next
header as that night's line-up (the event title). No times are given, so shows
default to 20:00; the year is inferred (nearest upcoming), and anything outside
a sane window is dropped (their list occasionally contains stale/typo'd dates).
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.kensingtonclub1935.com/calendar"

_WEEKDAYS = "Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday"
_MONTHS = ("January|February|March|April|May|June|July|August|September|"
           "October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec")
_HEADER = re.compile(
    r"(?:%s)\s*,?\s+(%s)\s+(\d{1,2})(?:st|nd|rd|th)?" % (_WEEKDAYS, _MONTHS), re.I)

# Stop collecting a line-up when we hit obvious page chrome.
_STOP = re.compile(r"bottom of page|opening hours|contact\b|find us|©|copyright", re.I)


def _best_blob(soup):
    """The tightest text block that still contains the whole 'Upcoming Shows' list."""
    candidates = []
    for el in soup.find_all(["section", "div"]):
        s = el.get_text(" ", strip=True)
        if "Upcoming Shows" in s and len(_HEADER.findall(s)) >= 3:
            candidates.append(s)
    if not candidates:
        return ""
    # smallest such block = least surrounding chrome
    return min(candidates, key=len)


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    blob = _best_blob(soup)
    i = blob.find("Upcoming Shows")
    if i >= 0:
        blob = blob[i + len("Upcoming Shows"):]

    matches = list(_HEADER.finditer(blob))
    events = []
    seen = set()
    lo = today - datetime.timedelta(days=3)
    hi = today + datetime.timedelta(days=160)

    for idx, m in enumerate(matches):
        month = common.month_to_num(m.group(1))
        if not month:
            continue
        d = common.infer_date(month, int(m.group(2)), today)
        if not d or d < lo or d > hi:
            continue

        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(blob)
        acts = blob[m.end():end]
        stop = _STOP.search(acts)
        if stop:
            acts = acts[:stop.start()]
        acts = re.sub(r"\s+", " ", acts).strip(" -–—|")
        if not acts:
            continue
        title = acts if len(acts) <= 90 else acts[:88].rstrip() + "…"

        key = (d.isoformat(), title.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "kensington-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:34]),
            "title": title,
            "date": d.isoformat(),
            "time": "20:00",
            "venue": "The Kensington Club",
            "category": "kensington",
            "price": "",
            "description": "",
            "url": URL,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Kensington Club: %d events" % len(evs))
    for e in evs:
        print("  ", e["date"], e["time"], "-", e["title"])
