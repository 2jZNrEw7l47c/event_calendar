"""Excel-backed failure log for scraper/build_events_data.py.

Tracks, across runs, which venues/flyer sources failed to update and how
many consecutive runs (with no successful run in between) each has failed
for. Two sheets in one workbook:
  Failures          - one row per source currently failing.
  Frequent Failures - the subset of Failures with consecutive_fails >= 3,
                       a signal the source site changed and the scraper
                       needs a rewrite.
"""

import os

import openpyxl

FREQUENT_FAIL_THRESHOLD = 3

_HEADERS = ["Venue", "Error Code", "Error Message", "Consecutive Fails", "Last Failed"]
_SHEET_FAILURES = "Failures"
_SHEET_FREQUENT = "Frequent Failures"

# Leading characters openpyxl/Excel treat as "this cell is a formula".
_INJECTION_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _excel_safe(value):
    """Prefix a value that Excel/openpyxl would otherwise interpret as a
    formula (leading =, +, -, @, tab, or CR) with a single quote, so it's
    stored as inert text rather than a live formula/DDE payload."""
    if isinstance(value, str) and value and value[0] in _INJECTION_PREFIXES:
        return "'" + value
    return value


def _unescape_excel_safe(value):
    """Undo _excel_safe's leading-quote guard when reading a value back."""
    if isinstance(value, str) and len(value) > 1 and value[0] == "'" \
            and value[1] in _INJECTION_PREFIXES:
        return value[1:]
    return value


def classify(exc):
    """Return (error_code, error_message) for a caught scraper exception."""
    response = getattr(exc, "response", None)
    status_code = getattr(response, "status_code", None) if response is not None else None
    if status_code is not None:
        return "HTTP %d" % status_code, str(exc)
    return type(exc).__name__, str(exc)


def load(path):
    """Read the Failures sheet into
    {venue: {error_code, error_message, consecutive_fails, last_failed}}.
    A missing or unreadable file is treated as an empty log."""
    if not os.path.exists(path):
        return {}
    try:
        wb = openpyxl.load_workbook(path)
        ws = wb[_SHEET_FAILURES]
    except Exception as exc:
        print("!! could not read %s: %s" % (path, exc))
        return {}

    log = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue
        venue, error_code, error_message, consecutive_fails, last_failed = row[:5]
        venue = _unescape_excel_safe(venue)
        log[venue] = {
            "error_code": _unescape_excel_safe(error_code),
            "error_message": _unescape_excel_safe(error_message),
            "consecutive_fails": int(consecutive_fails or 0),
            "last_failed": last_failed,
        }
    return log


def record_failure(log, venue, error_code, error_message, now):
    """Upsert venue's entry, bumping its consecutive-fail streak by 1."""
    prev = log.get(venue, {}).get("consecutive_fails", 0)
    log[venue] = {
        "error_code": error_code,
        "error_message": error_message,
        "consecutive_fails": prev + 1,
        "last_failed": now,
    }


def record_success(log, venue):
    """Drop venue from the log - a fresh future failure starts its streak
    over at 1."""
    log.pop(venue, None)


def save(path, log):
    """Write both sheets from the current log dict. Warns (doesn't raise)
    if the file can't be written, e.g. it's open in Excel, or a value
    contains characters Excel can't store."""
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = _SHEET_FAILURES
        ws.append(_HEADERS)
        for venue in sorted(log):
            entry = log[venue]
            ws.append([_excel_safe(venue), _excel_safe(entry["error_code"]),
                       _excel_safe(entry["error_message"]),
                       entry["consecutive_fails"], entry["last_failed"]])

        ws2 = wb.create_sheet(_SHEET_FREQUENT)
        ws2.append(_HEADERS)
        for venue in sorted(log):
            entry = log[venue]
            if entry["consecutive_fails"] >= FREQUENT_FAIL_THRESHOLD:
                ws2.append([_excel_safe(venue), _excel_safe(entry["error_code"]),
                            _excel_safe(entry["error_message"]),
                            entry["consecutive_fails"], entry["last_failed"]])

        wb.save(path)
    except Exception as exc:
        print("!! could not write %s: %s" % (path, exc))
