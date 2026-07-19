"""Shared parser for the Squarespace "day list" format used by the Blind Lady
Ale House family (Blind Lady, Panama 66 — same operators, same markup).

The page lists one <h3> per day ("Fri 7/17/26") followed by a paragraph mixing
opening hours with that night's act, e.g.:

    Food 11am-9pm / Bar 10pm THE BEARD & THE BIRD , 6-8pm

Acts are written in ALL CAPS, so we take the longest uppercase run as the act
and the time range that follows it (", 6-8pm") as the set time. Days whose
paragraph has no uppercase act (just hours / "closed") produce no event.
"""

import re
import datetime

import requests
from bs4 import BeautifulSoup

import common

_DAY = re.compile(r"^\w{3}\s+(\d{1,2})/(\d{1,2})/(\d{2})$")
# uppercase act runs; allow &, ', ., !, digits, spaces
_ACT = re.compile(r"\b([A-Z][A-Z0-9&'’\.\!\?\-]+(?:\s+[A-Z0-9&'’\.\!\?\-]+)*)")
_SKIP_TOKENS = {"FOOD", "BAR", "KITCHEN", "CLOSED", "OPEN", "AM", "PM", "TBA", "DJ", "DJS"}


def _clean_act(text):
    """Longest plausible uppercase run that isn't opening-hours chrome."""
    best = ""
    for m in _ACT.finditer(text):
        s = m.group(1).strip(" -–,.")
        words = [w for w in re.split(r"\s+", s) if w]
        words = [w for w in words if w.upper() not in _SKIP_TOKENS]
        # drop trailing time-ish tokens ("5-7", "6PM") and stray single letters
        while words and (re.fullmatch(r"\d{1,2}(?::\d{2})?(?:-\d{1,2}(?::\d{2})?)?(?:AM|PM)?", words[-1], re.I)
                         or len(words[-1]) == 1):
            words.pop()
        cand = " ".join(words).strip()
        if len(cand) > len(best) and len(cand) >= 4:
            best = cand
    return best


def scrape_daylist(url, venue, category, today=None, default_time="18:00"):
    today = today or datetime.date.today()
    resp = requests.get(url, headers=common.UA, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(common.decode(resp), "html.parser")

    events = []
    seen = set()
    for h3 in soup.find_all("h3"):
        m = _DAY.match(h3.get_text(" ", strip=True).replace("\xa0", " "))
        if not m:
            continue
        month, day, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            d = datetime.date(2000 + yy, month, day)
        except ValueError:
            continue
        if d < today:
            continue

        # gather text until the next day header
        parts = []
        sib = h3.find_next_sibling()
        while sib is not None and not (sib.name == "h3" and _DAY.match(sib.get_text(strip=True).replace("\xa0", " "))):
            parts.append(sib.get_text(" ", strip=True))
            sib = sib.find_next_sibling()
        blob = re.sub(r"\s+", " ", " ".join(parts)).strip()
        if not blob:
            continue

        act = _clean_act(blob)
        if not act:
            continue

        # time: prefer a range/time right after the act mention
        after = blob[blob.upper().find(act.split()[0]):]
        clock = common.parse_loose_time(after) or common.parse_loose_time(blob) or default_time

        key = (d.isoformat(), act.lower())
        if key in seen:
            continue
        seen.add(key)

        events.append({
            "id": "%s-%s-%s" % (category, d.isoformat(), re.sub(r"[^a-z0-9]+", "-", act.lower())[:30]),
            "title": act.title(),
            "date": d.isoformat(),
            "time": clock,
            "venue": venue,
            "category": category,
            "price": "",
            "description": blob[:140],
            "url": url,
        })
    return events
