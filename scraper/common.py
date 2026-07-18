"""Shared helpers for the venue scrapers: HTTP, date/time parsing, year inference."""

import re
import datetime

# A normal browser UA — some hosts return trimmed markup to unknown agents.
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0 Safari/537.36"}

_MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def decode(resp):
    """Decode a response body, tolerating the cp1252 some WP/Tribe sites emit.

    Try strict UTF-8 first (correct for most sites); if that fails on stray
    smart-quote / accented bytes, fall back to windows-1252.
    """
    raw = resp.content
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def month_to_num(token):
    """'Jan', 'Sept.', 'July' -> 1..12, or None."""
    if not token:
        return None
    return _MONTHS.get(token.strip().strip(".").lower())


def infer_date(month, day, today):
    """Neither site prints a year, so pick the nearest upcoming occurrence.

    Dates up to 14 days in the past keep the current year (a show that just
    happened is still worth listing/dimming); anything older rolls to next year
    (e.g. a 'Jan 10' listing seen in July is next January).
    Returns a datetime.date, or None if the day is invalid.
    """
    for year in (today.year, today.year + 1):
        try:
            d = datetime.date(year, month, day)
        except ValueError:
            return None
        if (today - d).days <= 14:
            return d
    # month/day earlier in the year than today by a lot -> next year
    return datetime.date(today.year + 1, month, day)


def _to_24h(hour, minute, ampm):
    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    return "%02d:%02d" % (hour, minute)


def parse_clock(text):
    """Parse an explicit clock string like '4:00PM' or '8 PM' -> '16:00' / '20:00'."""
    if not text:
        return None
    s = text.lower()
    m = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)", s)
    if m:
        return _to_24h(int(m.group(1)), int(m.group(2)), m.group(3))
    m = re.search(r"(\d{1,2})\s*(am|pm)", s)
    if m:
        return _to_24h(int(m.group(1)), 0, m.group(2))
    return None


def parse_loose_time(text):
    """Best-effort parse of McGuffie's hand-typed times.

    Handles '8pm', '2pm', '4-7pm', '9:45-2am' (returns the start time, 24h).
    am/pm is often missing on the start of a range, so we infer:
      * a trailing 'pm' in the string applies to the start ('4-7pm' -> 4pm)
      * a trailing 'am' with a start hour >= 6 means a night show crossing
        midnight ('9:45-2am' -> 9:45pm)
      * with no am/pm at all, hours 4..11 are read as evening (pm), a sane
        default for a live-music room.
    Returns 'HH:MM' or None.
    """
    if not text:
        return None
    s = text.lower().replace(".", "")
    first = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", s)
    if not first:
        return None
    hour = int(first.group(1))
    minute = int(first.group(2) or 0)
    ampm = first.group(3)

    if not ampm:
        trailing = re.findall(r"(am|pm)", s)
        if trailing:
            if trailing[0] == "pm":
                ampm = "pm"
            else:  # trailing 'am' -> only pm if the start hour is late evening
                ampm = "pm" if hour >= 6 else "am"
        else:
            ampm = "pm" if 4 <= hour <= 11 else "am"

    if hour > 12:
        return None
    return _to_24h(hour, minute, ampm)
