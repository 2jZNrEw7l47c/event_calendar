"""Shared helper for venues whose site embeds a DICE event-list widget
(e.g. Banshee Bar). The widget calls DICE's public partner API; we call the same
endpoint with the widget's own public api key + promoter filter.

The widget config (api key + promoter name) is embedded in the venue's page as
    DiceEventListWidget.create({... "apiKey": "...", "promoters": ["..."] ...})
so a per-venue scraper just passes those in.

DICE returns event start times in UTC; we convert to America/Los_Angeles.
"""

import datetime

import requests

import common

API = "https://partners-endpoint.dice.fm/api/v2/events"

try:
    from zoneinfo import ZoneInfo
    _PACIFIC = ZoneInfo("America/Los_Angeles")
except Exception:            # pragma: no cover - fallback if tz db missing
    _PACIFIC = None


def _pacific(iso):
    """'2026-07-18T03:00:00Z' -> ('2026-07-17', '20:00') in San Diego time."""
    try:
        dt = datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        return None, None
    dt = dt.replace(tzinfo=datetime.timezone.utc)
    if _PACIFIC is not None:
        loc = dt.astimezone(_PACIFIC)
    else:
        # crude US Pacific DST: PDT (UTC-7) 2nd Sun Mar .. 1st Sun Nov, else PST
        offset = -7 if 3 <= dt.month <= 10 else -8
        loc = dt.astimezone(datetime.timezone(datetime.timedelta(hours=offset)))
    return loc.date().isoformat(), "%02d:%02d" % (loc.hour, loc.minute)


def scrape_dice(api_key, promoter, venue, category, today=None, page_size=50):
    today = today or datetime.date.today()
    headers = dict(common.UA)
    headers["x-api-key"] = api_key
    params = {
        "page[size]": str(page_size),
        "types": "linkout,event",
        "filter[promoter_name]": promoter,
    }
    resp = requests.get(API, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    events = []
    seen = set()
    for e in data:
        name = (e.get("name") or "").strip()
        if not name:
            continue
        # Drop sold-out and cancelled shows (DICE exposes both explicitly).
        if e.get("sold_out") or e.get("status") == "cancelled":
            continue
        date, time = _pacific(e.get("date"))
        if not date:
            continue
        if date < today.isoformat():
            continue
        key = (date, name.lower())
        if key in seen:
            continue
        seen.add(key)

        # price: lowest ticket price if present
        price = ""
        tt = e.get("ticket_types") or []
        prices = [t.get("price", {}).get("total") for t in tt if isinstance(t.get("price"), dict)] if isinstance(tt, list) else []
        prices = [p for p in prices if isinstance(p, (int, float)) and p > 0]
        if prices:
            price = "$%.2f" % (min(prices) / 100.0)

        events.append({
            "id": "%s-%s-%s" % (category, date, (e.get("checksum") or name)[:16]),
            "title": name,
            "date": date,
            "time": time or "20:00",
            "venue": venue,
            "category": category,
            "price": price,
            "description": "",
            "url": e.get("url") or "",
        })
    return events
