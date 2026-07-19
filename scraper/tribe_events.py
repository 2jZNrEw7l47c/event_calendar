"""Shared helper for WordPress sites running "The Events Calendar" (Tribe),
which exposes a clean REST API at /wp-json/tribe/events/v1/events.

A per-venue scraper is then a one-liner (see scrape_whistlestop.py).
"""

import re
import html
import datetime

import requests

import common

HORIZON_DAYS = 120     # don't pull events more than ~4 months out
MAX_PAGES = 6          # safety cap (per_page=50 -> up to 300 events)
PER_PAGE = 50


def _strip_html(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = s.replace("�", "")   # drop replacement chars baked into source data
    return re.sub(r"\s+", " ", s).strip()


def scrape_tribe(base_url, venue, category, today=None):
    today = today or datetime.date.today()
    end = today + datetime.timedelta(days=HORIZON_DAYS)
    api = base_url.rstrip("/") + "/wp-json/tribe/events/v1/events"
    params = {
        "per_page": PER_PAGE,
        "start_date": today.isoformat(),
        "end_date": end.isoformat(),
    }

    events = []
    seen = set()
    url = api
    for _ in range(MAX_PAGES):
        try:
            resp = requests.get(url, headers=common.UA, params=params, timeout=75)
        except (requests.Timeout, requests.ConnectionError):
            # Some of these WP hosts are slow/flaky; one retry rescues most runs.
            resp = requests.get(url, headers=common.UA, params=params, timeout=75)
        if resp.status_code != 200:
            break
        import json
        data = json.loads(common.decode(resp))
        for e in data.get("events", []):
            det = e.get("start_date_details") or {}
            if not det:
                continue
            date = "%s-%s-%s" % (det.get("year"), det.get("month"), det.get("day"))
            time = "%s:%s" % (det.get("hour", "20"), det.get("minutes", "00"))
            title = _strip_html(e.get("title")) or "(untitled)"
            key = (date, title)
            if key in seen:
                continue
            seen.add(key)
            desc = _strip_html(e.get("excerpt"))[:200]
            events.append({
                "id": "%s-%s-%s" % (category, date, re.sub(r"[^a-z0-9]+", "-", title.lower())[:36]),
                "title": title,
                "date": date,
                "time": time,
                "venue": venue,
                "category": category,
                "price": _strip_html(e.get("cost")),
                "description": desc,
                "url": e.get("url") or base_url,
            })
        # follow pagination if present
        nxt = data.get("next_rest_url")
        if not nxt:
            break
        url, params = nxt, None
    return events
