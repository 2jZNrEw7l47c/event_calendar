"""Winston's Beach Club (winstonsob.com) — Drupal 7 site.

The homepage server-renders the upcoming schedule as Drupal views rows: each
row has the date+time in <span class="date-display-single"> ("Sat, Jul 18 -
2:00 PM") inside an h4 link, and the event title in a following <strong><a>.
No year is printed (a month heading like "July 2026" sits above), so the year
is inferred like the other text venues.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://winstonsob.com/"


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for row in soup.select("div[class*=views-row]"):
        date_el = row.select_one(".date-display-single")
        title_el = row.select_one("strong a")
        if not (date_el and title_el):
            continue

        date_text = date_el.get_text(" ", strip=True)      # "Sat, Jul 18 - 2:00 PM"
        m = re.search(r"([A-Za-z]+)\s+(\d{1,2})", date_text.split(",")[-1])
        if not m:
            continue
        month = common.month_to_num(m.group(1))
        if not month:
            continue
        d = common.infer_date(month, int(m.group(2)), today)
        if not d or d < today:
            continue

        clock = common.parse_clock(date_text) or "20:00"
        title = title_el.get_text(" ", strip=True)
        if not title:
            continue

        href = title_el.get("href") or ""
        url = href if href.startswith("http") else ("https://winstonsob.com" + href) if href else URL

        key = (d.isoformat(), clock, title.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "winstons-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:34]),
            "title": title,
            "date": d.isoformat(),
            "time": clock,
            "venue": "Winston's",
            "category": "winstons",
            "price": "",
            "description": "",
            "url": url,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Winston's: %d events" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], e["time"], "-", e["title"])
