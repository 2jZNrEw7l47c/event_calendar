"""Cal Coast Credit Union Open Air Theatre, SDSU (as.sdsu.edu/calcoast).

Server-rendered cards: <div class="card-body"> with <p class="card-date">
"Tue, Jul 21, 2026, 8pm" followed by the act name. Ticketing is Ticketmaster,
but the listing itself is plain HTML.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://as.sdsu.edu/calcoast/events"


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for card in soup.select("div.card-body"):
        dp = card.select_one("p.card-date")
        if not dp:
            continue
        text = dp.get_text(" ", strip=True)      # "Tue, Jul 21, 2026, 8pm"
        m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", text)
        if not m:
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
        clock = common.parse_loose_time(text.split(",")[-1]) or "19:30"

        title = re.sub(r"\s+", " ", card.get_text(" ", strip=True).replace(text, "")).strip()
        if not title:
            continue

        a = card.find("a", href=True) or (card.parent.find("a", href=True) if card.parent else None)
        url = a["href"] if a else URL
        if url.startswith("/"):
            url = "https://as.sdsu.edu" + url

        key = (d.isoformat(), title.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "calcoast-%s-%s" % (d.isoformat(), re.sub(r"[^a-z0-9]+", "-", title.lower())[:30]),
            "title": title,
            "date": d.isoformat(),
            "time": clock,
            "venue": "Cal Coast Open Air Theatre",
            "category": "calcoast",
            "price": "",
            "description": "",
            "url": url,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Cal Coast: %d events" % len(evs))
    for e in evs[:8]:
        print("  ", e["date"], e["time"], "-", e["title"])
