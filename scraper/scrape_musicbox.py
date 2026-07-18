"""Music Box (musicboxsd.com) — WordPress + TicketWeb, but a different theme
than the Belly Up / The Sound plugin: /shows/ server-renders each show as an
<article class="event-card"> with the date in .date ("Sat, Jul 18"), the acts
as .tw-artist spans (billing-1_00 = headliner, lower billings = support), an
optional .topline presenter, and a ticket button whose text flips to
"Cancelled" / "Sold Out" when applicable — we skip those.

No time is printed; shows default to 20:00. No year either, so it's inferred.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

URL = "https://musicboxsd.com/shows/"


def scrape(today=None):
    today = today or datetime.date.today()
    resp = requests.get(URL, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for card in soup.select("article.event-card"):
        btn = card.select_one(".wp-block-button a")
        btn_text = btn.get_text(" ", strip=True).lower() if btn else ""
        if "cancel" in btn_text or "sold out" in btn_text:
            continue

        date_el = card.select_one(".date")
        if not date_el:
            continue
        m = re.search(r"([A-Za-z]+)\s+(\d{1,2})", date_el.get_text(" ", strip=True).split(",")[-1])
        if not m:
            continue
        month = common.month_to_num(m.group(1))
        if not month:
            continue
        d = common.infer_date(month, int(m.group(2)), today)
        if not d or d < today:
            continue

        artists = card.select(".tw-artist")
        heads, support = [], []
        for a in artists:
            cls = " ".join(a.get("class", []))
            (heads if "billing-1_00" in cls else support).append(a.get_text(" ", strip=True))
        heads = [h for h in dict.fromkeys(heads) if h]
        support = [s for s in dict.fromkeys(support) if s]
        if not heads and not support:
            continue
        title = ", ".join(heads) or support.pop(0)

        topline = card.select_one(".topline")
        desc_bits = []
        if topline and topline.get_text(strip=True):
            desc_bits.append(topline.get_text(" ", strip=True))
        if support:
            desc_bits.append("With " + ", ".join(support))
        description = " · ".join(desc_bits)

        link = card.select_one("a.image-url") or btn
        url = link["href"] if link and link.has_attr("href") else URL
        mid = re.search(r"/event/(\d+)/", url)
        event_id = mid.group(1) if mid else None

        key = (d.isoformat(), title.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "musicbox-%s" % (event_id or (d.isoformat() + "-" + re.sub(r"[^a-z0-9]+", "-", title.lower())[:30])),
            "title": title,
            "date": d.isoformat(),
            "time": "20:00",
            "venue": "Music Box",
            "category": "musicbox",
            "price": "",
            "description": description,
            "url": url,
        })
    return events


if __name__ == "__main__":
    evs = scrape()
    print("Music Box: %d events" % len(evs))
    for e in evs[:10]:
        print("  ", e["date"], "-", e["title"], "|", e["description"][:40])
