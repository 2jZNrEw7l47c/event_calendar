"""KPBS community events calendar (kpbs.org/events/all) — aggregator.

Server-rendered promo blocks with EventPromoC-* classes: the next occurrence
in "EventPromoC-recurring-date" ("Monday, July 20, 2026 at 7:45 PM") or a
"EventPromoC-time-text" span, the title in the block's heading/link, and often
a venue line. Aggregator policy: build-level dedup drops any KPBS event whose
(date, title) matches an event from an actual venue scraper.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://www.kpbs.org/events/all"

_DATE = re.compile(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})(?:\s+at\s+(.+))?")


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=40)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    # promo containers: the nearest ancestor holding both a date element and
    # a link — walk up from each recurring-date/time-text element
    date_els = soup.select("[class*='EventPromoC-recurring-date'], [class*='EventPromoC-time-text']")
    events = []
    seen = set()
    for de in date_els:
        text = de.get_text(" ", strip=True)
        m = _DATE.search(text)
        if not m or text.lower().startswith("ongoing"):
            continue
        month = common.month_to_num(m.group(1))
        if not month:
            continue
        try:
            d = datetime.date(int(m.group(3)), month, int(m.group(2)))
        except ValueError:
            continue
        if d < today:
            continue
        clock = common.parse_clock(m.group(4) or "") or "19:00"

        cont = de
        title = ""
        url = URL
        venue = ""
        for _ in range(6):
            cont = cont.parent
            if cont is None:
                break
            head = cont.select_one("[class*='EventPromoC-title'] a, [class*='EventPromoC-title'], h2 a, h3 a")
            if head:
                title = head.get_text(" ", strip=True)
                a = head if head.name == "a" else head.find("a", href=True)
                if a and a.has_attr("href"):
                    url = a["href"]
                ven = cont.select_one("[class*='EventPromoC-venue'], [class*='venue']")
                if ven:
                    venue = ven.get_text(" ", strip=True)[:60]
                break
        if not title:
            continue
        if url.startswith("/"):
            url = "https://www.kpbs.org" + url

        key = (d.isoformat(), title.lower())
        if key in seen:
            continue
        seen.add(key)
        events.append({
            "id": "kpbs-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:30]),
            "title": title,
            "date": d.isoformat(),
            "time": clock,
            "venue": "KPBS calendar",
            "category": "kpbs",
            "price": "",
            "description": venue,
            "url": url,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("KPBS: %d events" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], e["time"], "-", e["title"][:45], "@", e["description"][:30])
