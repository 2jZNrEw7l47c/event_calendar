"""Del Mar Fairgrounds / Del Mar Thoroughbred Club (dmtc.com/calendar).

The calendar is a server-rendered month grid. Each td.calendar-month-day holds
the day number plus that day's items: racing chrome ("11 Races", Gates, First
Post, trophy-flagged stakes in .text-warning) and special events in
.text-success spans (festivals, concerts, parties).

Per site policy we keep ONLY the special events and drop everything
racing-related — both structurally (.text-success only) and by keyword, since
some racing-adjacent items (wagering seminars, Daybreak workouts) are styled
as specials. The Sound (concert venue at the fairgrounds) is scraped
separately; build-level dedup prefers The Sound's copy.

Only the current month is served statically; each scrape captures the month
in view.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.dmtc.com/calendar"

_RACING = re.compile(
    r"\b(rac(?:e|es|ing)|wagering|handicap|stakes|first post|opening day|"
    r"daybreak|seabiscuit|pony party|turf club)\b", re.I)


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=35)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    heading = soup.find(string=re.compile(
        r"^(January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+\d{4}$"))
    if not heading:
        return []
    month = common.month_to_num(heading.split()[0])
    year = int(heading.split()[1])

    events = []
    seen = set()
    seen_first = False
    for cell in soup.select("td.calendar-month-day"):
        date_el = cell.select_one(".calendar-date")
        if not date_el:
            continue
        # strip the mobile-only "Sat," / "th" spans around the day number
        num = re.sub(r"[^\d]", "", "".join(
            s for s in date_el.find_all(string=True, recursive=False)))
        if not num:
            m = re.search(r"\d{1,2}", date_el.get_text())
            num = m.group(0) if m else ""
        if not num:
            continue
        day = int(num)
        # leading/trailing cells belong to adjacent months: skip until day 1
        # appears, and stop once the sequence resets
        if day == 1:
            if seen_first:
                break
            seen_first = True
        if not seen_first:
            continue

        try:
            d = datetime.date(year, month, day)
        except ValueError:
            continue
        if d < today:
            continue

        for sp in cell.select(".text-success"):
            title = sp.get_text(" ", strip=True)
            if not title or _RACING.search(title):
                continue
            a = sp.find("a", href=True) or (sp.find_parent("a", href=True))
            url = a["href"] if a else URL
            if url.startswith("/"):
                url = "https://www.dmtc.com" + url

            key = (d.isoformat(), title.lower())
            if key in seen:
                continue
            seen.add(key)
            events.append({
                "id": "delmar-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:30]),
                "title": title,
                "date": d.isoformat(),
                "time": "14:00",
                "venue": "Del Mar Fairgrounds",
                "category": "delmar",
                "price": "",
                "description": "During live racing season — gate times on dmtc.com",
                "url": url,
            })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Del Mar: %d events" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], "-", e["title"])
