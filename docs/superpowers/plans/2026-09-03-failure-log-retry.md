# Scraper Failure Log & Retry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `scraper/build_events_data.py` a persistent, per-source failure log (Excel workbook) with an automatic once-per-run retry, and the exact terminal output the user specified.

**Architecture:** A new standalone module `scraper/failure_log.py` owns the Excel I/O (load/record/save, two sheets: `Failures` and `Frequent Failures`) and is fully unit-testable with no network or Excel file needed for most tests. `build_events_data.py` gets a new `_run_with_retry(items, today, now, log, newly_frequent)` helper that runs a list of `(label, fn)` pairs, retries failures once, and updates the log — used for both the 44 venue scrapers and the 2 flyer scrapers. It's testable in isolation with fake `fn` callables (no network).

**Tech Stack:** Python 3.13, `openpyxl` (new dependency, already present in this environment), `pytest` (already present), existing `requests`/`bs4` scraper stack unchanged.

Full context: [docs/superpowers/specs/2026-09-03-failure-log-retry-design.md](../specs/2026-09-03-failure-log-retry-design.md)

---

### Task 1: Add the `openpyxl` dependency

**Files:**
- Modify: `scraper/requirements.txt`

- [ ] **Step 1: Add the dependency**

Add a line to `scraper/requirements.txt` so it reads:

```
requests>=2.31
beautifulsoup4>=4.12
openpyxl>=3.1
```

- [ ] **Step 2: Verify it's importable**

Run: `python -c "import openpyxl; print(openpyxl.__version__)"`
Expected: prints a version like `3.1.5` (already installed in this environment; this just confirms the pin is satisfied).

- [ ] **Step 3: Commit**

```bash
git add scraper/requirements.txt
git commit -m "Add openpyxl dependency for scraper failure log"
```

---

### Task 2: `scraper/failure_log.py` — the Excel-backed log

**Files:**
- Create: `scraper/failure_log.py`
- Create: `scraper/test_failure_log.py`

- [ ] **Step 1: Write the failing tests**

Create `scraper/test_failure_log.py`:

```python
import openpyxl

import failure_log


def test_record_failure_starts_streak_at_one():
    log = {}
    failure_log.record_failure(log, "Casbah", "HTTP 500", "server error",
                                "2026-09-03 10:00")
    assert log["Casbah"]["consecutive_fails"] == 1


def test_record_failure_increments_existing_streak():
    log = {"Casbah": {"error_code": "HTTP 500", "error_message": "server error",
                       "consecutive_fails": 4, "last_failed": "2026-09-02 10:00"}}
    failure_log.record_failure(log, "Casbah", "HTTP 500", "server error",
                                "2026-09-03 10:00")
    assert log["Casbah"]["consecutive_fails"] == 5
    assert log["Casbah"]["last_failed"] == "2026-09-03 10:00"


def test_record_success_clears_entry():
    log = {"Casbah": {"error_code": "HTTP 500", "error_message": "server error",
                       "consecutive_fails": 3, "last_failed": "2026-09-02 10:00"}}
    failure_log.record_success(log, "Casbah")
    assert "Casbah" not in log


def test_record_success_on_absent_venue_is_a_noop():
    log = {}
    failure_log.record_success(log, "Casbah")
    assert log == {}


def test_classify_http_error_uses_status_code():
    class FakeResponse:
        status_code = 404

    class FakeHTTPError(Exception):
        def __init__(self):
            super().__init__("404 Client Error")
            self.response = FakeResponse()

    code, message = failure_log.classify(FakeHTTPError())
    assert code == "HTTP 404"
    assert message == "404 Client Error"


def test_classify_generic_exception_uses_type_name():
    code, message = failure_log.classify(ConnectionError("boom"))
    assert code == "ConnectionError"
    assert message == "boom"


def test_load_missing_file_returns_empty_dict(tmp_path):
    path = str(tmp_path / "failure_log.xlsx")
    assert failure_log.load(path) == {}


def test_save_then_load_round_trip(tmp_path):
    path = str(tmp_path / "failure_log.xlsx")
    log = {"Casbah": {"error_code": "HTTP 500", "error_message": "server error",
                       "consecutive_fails": 2, "last_failed": "2026-09-03 10:00"}}
    failure_log.save(path, log)

    loaded = failure_log.load(path)
    assert loaded == log


def test_save_writes_frequent_failures_sheet_filtered_by_threshold(tmp_path):
    path = str(tmp_path / "failure_log.xlsx")
    log = {
        "Casbah": {"error_code": "HTTP 500", "error_message": "server error",
                   "consecutive_fails": 5, "last_failed": "2026-09-03 10:00"},
        "Soda Bar": {"error_code": "Timeout", "error_message": "timed out",
                     "consecutive_fails": 2, "last_failed": "2026-09-03 10:00"},
    }
    failure_log.save(path, log)

    wb = openpyxl.load_workbook(path)
    ws = wb["Frequent Failures"]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    assert [r[0] for r in rows] == ["Casbah"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest scraper/test_failure_log.py -v`
Expected: FAIL/ERROR for every test with `ModuleNotFoundError: No module named 'failure_log'` (the module doesn't exist yet).

- [ ] **Step 3: Write the implementation**

Create `scraper/failure_log.py`:

```python
"""Excel-backed failure log for scraper/build_events_data.py.

Tracks, across runs, which venues/flyer sources failed to update and how
many consecutive runs (with no successful run in between) each has failed
for. Two sheets in one workbook:
  Failures          - one row per source currently failing.
  Frequent Failures - the subset of Failures with consecutive_fails >= 5,
                       a signal the source site changed and the scraper
                       needs a rewrite.
"""

import os

import openpyxl

FREQUENT_FAIL_THRESHOLD = 5

_HEADERS = ["Venue", "Error Code", "Error Message", "Consecutive Fails", "Last Failed"]
_SHEET_FAILURES = "Failures"
_SHEET_FREQUENT = "Frequent Failures"


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
    except Exception:
        return {}

    log = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue
        venue, error_code, error_message, consecutive_fails, last_failed = row[:5]
        log[venue] = {
            "error_code": error_code,
            "error_message": error_message,
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
    if the file can't be written, e.g. it's open in Excel."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = _SHEET_FAILURES
    ws.append(_HEADERS)
    for venue in sorted(log):
        entry = log[venue]
        ws.append([venue, entry["error_code"], entry["error_message"],
                   entry["consecutive_fails"], entry["last_failed"]])

    ws2 = wb.create_sheet(_SHEET_FREQUENT)
    ws2.append(_HEADERS)
    for venue in sorted(log):
        entry = log[venue]
        if entry["consecutive_fails"] >= FREQUENT_FAIL_THRESHOLD:
            ws2.append([venue, entry["error_code"], entry["error_message"],
                        entry["consecutive_fails"], entry["last_failed"]])

    try:
        wb.save(path)
    except OSError as exc:
        print("!! could not write %s: %s" % (path, exc))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest scraper/test_failure_log.py -v`
Expected: PASS — all 9 tests green.

- [ ] **Step 5: Commit**

```bash
git add scraper/failure_log.py scraper/test_failure_log.py
git commit -m "Add Excel-backed failure log for the scraper run"
```

---

### Task 3: Wire retry + logging into `build_events_data.py`

**Files:**
- Modify: `scraper/build_events_data.py`
- Create: `scraper/test_build_events_data.py`

- [ ] **Step 1: Write the failing tests for `_run_with_retry`**

Create `scraper/test_build_events_data.py`:

```python
import datetime

import build_events_data as bed

TODAY = datetime.date(2026, 9, 3)
NOW = "2026-09-03 10:00"


def test_success_on_first_try_no_retry_no_log_entry(capsys):
    def ok(today):
        return ["event"]

    log = {}
    newly_frequent = []
    results = bed._run_with_retry([("Casbah", ok)], TODAY, NOW, log, newly_frequent)

    assert results == {"Casbah": ["event"]}
    assert log == {}
    assert newly_frequent == []
    out = capsys.readouterr().out
    assert "Updating Casbah.." in out
    assert "Retrying" not in out


def test_fails_then_succeeds_on_retry_clears_any_prior_streak(capsys):
    calls = {"n": 0}

    def flaky(today):
        calls["n"] += 1
        if calls["n"] == 1:
            raise ConnectionError("boom")
        return ["event"]

    log = {"Casbah": {"error_code": "ConnectionError", "error_message": "boom",
                       "consecutive_fails": 3, "last_failed": "2026-09-02 10:00"}}
    newly_frequent = []
    results = bed._run_with_retry([("Casbah", flaky)], TODAY, NOW, log, newly_frequent)

    assert results == {"Casbah": ["event"]}
    assert "Casbah" not in log
    out = capsys.readouterr().out
    assert "Updating Casbah.." in out
    assert "Retrying Casbah.." in out


def test_fails_both_times_logs_the_failure(capsys):
    def always_fails(today):
        raise ConnectionError("boom")

    log = {}
    newly_frequent = []
    results = bed._run_with_retry([("Casbah", always_fails)], TODAY, NOW, log, newly_frequent)

    assert results == {"Casbah": None}
    assert log["Casbah"]["consecutive_fails"] == 1
    assert log["Casbah"]["error_code"] == "ConnectionError"
    assert log["Casbah"]["last_failed"] == NOW
    out = capsys.readouterr().out
    assert "!! Casbah failed: boom" in out


def test_flags_newly_frequent_failure_only_once():
    def always_fails(today):
        raise ConnectionError("boom")

    log = {"Casbah": {"error_code": "ConnectionError", "error_message": "boom",
                       "consecutive_fails": 4, "last_failed": "2026-09-02 10:00"}}
    newly_frequent = []
    bed._run_with_retry([("Casbah", always_fails)], TODAY, NOW, log, newly_frequent)
    assert log["Casbah"]["consecutive_fails"] == 5
    assert newly_frequent == ["Casbah"]

    # A second run that also fails both attempts must not re-flag it.
    newly_frequent2 = []
    bed._run_with_retry([("Casbah", always_fails)], TODAY, NOW, log, newly_frequent2)
    assert log["Casbah"]["consecutive_fails"] == 6
    assert newly_frequent2 == []


def test_multiple_items_are_independent(capsys):
    def ok(today):
        return ["event"]

    def always_fails(today):
        raise ConnectionError("boom")

    log = {}
    newly_frequent = []
    results = bed._run_with_retry(
        [("Casbah", ok), ("Soda Bar", always_fails)], TODAY, NOW, log, newly_frequent)

    assert results == {"Casbah": ["event"], "Soda Bar": None}
    assert "Casbah" not in log
    assert log["Soda Bar"]["consecutive_fails"] == 1
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest scraper/test_build_events_data.py -v`
Expected: FAIL/ERROR — `AttributeError: module 'build_events_data' has no attribute '_run_with_retry'` (the function doesn't exist yet).

- [ ] **Step 3: Add the `failure_log` import and `LOG_PATH` constant**

In `scraper/build_events_data.py`, add to the import block (after the other `scrape_*` imports, around line 63):

```python
import scrape_kpbs

import failure_log
```

Add `LOG_PATH` next to the other path constants (around line 159-161, after `JSON_OUT`):

```python
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS_OUT = os.path.join(ROOT, "js", "events-data.js")
JSON_OUT = os.path.join(ROOT, "data", "events.json")
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "failure_log.xlsx")
```

- [ ] **Step 4: Add the `_run_with_retry` helper**

Add this function after `_identity` and before `_stamp_added` (around line 217, right after the `_identity` function ends):

```python
def _run_with_retry(items, today, now, log, newly_frequent):
    """Run each (label, fn) once, retry failures once, and keep `log` (a
    failure_log dict) in sync. Returns {label: result}, with result None for
    any label still failing after its retry. Appends to `newly_frequent` the
    label of any source whose consecutive-fail streak just crossed
    failure_log.FREQUENT_FAIL_THRESHOLD on this call."""
    results = {}
    pending = []
    for label, fn in items:
        print("Updating %s.." % label)
        try:
            result = fn(today)
        except Exception:
            pending.append((label, fn))
            continue
        failure_log.record_success(log, label)
        results[label] = result

    for label, fn in pending:
        print("Retrying %s.." % label)
        try:
            result = fn(today)
        except Exception as exc:
            error_code, error_message = failure_log.classify(exc)
            was_frequent = (log.get(label, {}).get("consecutive_fails", 0)
                            >= failure_log.FREQUENT_FAIL_THRESHOLD)
            failure_log.record_failure(log, label, error_code, error_message, now)
            if not was_frequent and (log[label]["consecutive_fails"]
                                      >= failure_log.FREQUENT_FAIL_THRESHOLD):
                newly_frequent.append(label)
            print("!! %s failed: %s" % (label, exc))
            results[label] = None
            continue
        failure_log.record_success(log, label)
        results[label] = result

    return results
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest scraper/test_build_events_data.py -v`
Expected: PASS — all 5 tests green.

- [ ] **Step 6: Commit**

```bash
git add scraper/build_events_data.py scraper/test_build_events_data.py
git commit -m "Add _run_with_retry helper for scraper failure retry"
```

- [ ] **Step 7: Wire `_run_with_retry` into the venue loop**

Replace the venue-scraping block in `main()` (currently):

```python
    excluded = 0
    for key, label, module in SCRAPERS:
        try:
            # entries are usually modules exposing scrape(); bare callables
            # (e.g. scrape_moonshine.scrape_beach) are accepted too
            fn = getattr(module, "scrape", module)
            evs = fn(today)
        except Exception as exc:                       # keep other venues if one fails
            print("!! %s failed: %s" % (label, exc))
            evs = []
        kept = [e for e in evs if not _excluded(e)]
        excluded += len(evs) - len(kept)
        per_venue[label] = len(kept)
        if kept:
            categories[key] = label
            all_events.extend(kept)
```

with:

```python
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    log = failure_log.load(LOG_PATH)
    newly_frequent = []

    # entries are usually modules exposing scrape(); bare callables
    # (e.g. scrape_moonshine.scrape_beach) are accepted too
    venue_items = [(label, getattr(module, "scrape", module)) for key, label, module in SCRAPERS]
    venue_results = _run_with_retry(venue_items, today, now, log, newly_frequent)

    excluded = 0
    for key, label, module in SCRAPERS:
        evs = venue_results.get(label)
        if evs is None:                                 # still failing after retry
            continue
        kept = [e for e in evs if not _excluded(e)]
        excluded += len(evs) - len(kept)
        per_venue[label] = len(kept)
        if kept:
            categories[key] = label
            all_events.extend(kept)
```

- [ ] **Step 8: Wire `_run_with_retry` into the flyer loop**

Replace the flyer block (currently):

```python
    # Image-only venues: fetch each flyer.
    flyers = []
    for label, module in FLYER_SCRAPERS:
        try:
            info = module.scrape(today)
        except Exception as exc:
            print("!! %s flyer failed: %s" % (label, exc))
            info = None
        if info:
            info = dict(info, venue=label)
            flyers.append(info)
```

with:

```python
    # Image-only venues: fetch each flyer.
    flyer_items = [(label, module.scrape) for label, module in FLYER_SCRAPERS]
    flyer_results = _run_with_retry(flyer_items, today, now, log, newly_frequent)

    flyers = []
    for label, module in FLYER_SCRAPERS:
        info = flyer_results.get(label)
        if info:
            flyers.append(dict(info, venue=label))

    failure_log.save(LOG_PATH, log)
    for flagged in newly_frequent:
        print("!! %s has failed 5+ runs in a row - script may need a rewrite" % flagged)
```

Note: this folds flyer failures into the same retry/logging machinery as venues, so a flyer failure now prints `!! {label} failed: {exc}` (via `_run_with_retry`) instead of the old `!! {label} flyer failed: {exc}` wording — consistent with every other source.

- [ ] **Step 9: Add the closing terminal output**

At the very end of `main()`, after the existing `for fl in flyers: print(...)` loop, add:

```python
    still_failing = sorted(log)
    print()
    if still_failing:
        print("failures:")
        for label in still_failing:
            print(label)
    else:
        print("failures: none")
    print()
    print("the updates are available here: https://2jznrew7l47c.github.io/event_calendar/")
```

- [ ] **Step 10: Re-run both test files to confirm nothing broke**

Run: `python -m pytest scraper/test_build_events_data.py scraper/test_failure_log.py -v`
Expected: PASS — all 14 tests green.

- [ ] **Step 11: Commit**

```bash
git add scraper/build_events_data.py
git commit -m "Wire failure-log retry into venue and flyer scraping"
```

---

### Task 4: End-to-end smoke test

**Files:** none (verification only)

- [ ] **Step 1: Run the real build**

Run: `python scraper/build_events_data.py`

Confirm in the output:
- A `Updating {label}..` line for every venue and flyer source, in order.
- Any source that failed its first attempt gets a `Retrying {label}..` line.
- A source still failing after retry prints `!! {label} failed: ...`.
- The output ends with a `failures:` block (or `failures: none`) followed by
  `the updates are available here: https://2jznrew7l47c.github.io/event_calendar/`.

If every source succeeds (likely, since these are generally stable feeds),
`failures: none` is expected and correct — that's not a test failure.

- [ ] **Step 2: Inspect the generated log**

Run: `python -c "import openpyxl; wb = openpyxl.load_workbook('scraper/failure_log.xlsx'); print(wb.sheetnames); [print(r) for r in wb['Failures'].iter_rows(values_only=True)]"`

Expected: sheet names `['Failures', 'Frequent Failures']`; the `Failures` sheet has a header row plus one row per source still failing after this run's retry (possibly zero rows, if everything succeeded).

- [ ] **Step 3: Confirm the site's data files still built correctly**

Run: `git status --short`
Expected: `js/events-data.js`, `data/events.json`, and `scraper/failure_log.xlsx` show as modified/new — the normal output of a build, now with the log file alongside it.

- [ ] **Step 4: Commit the generated log** (only if you want this particular
  run's log committed — normally `update-events.bat` handles this as part of
  its existing `git add -A` / commit / push flow)

```bash
git add scraper/failure_log.xlsx
git commit -m "Record scraper failure log from smoke-test run"
```

If `js/events-data.js` and `data/events.json` also changed from this smoke
test run and you don't want that data refresh committed separately, leave
them unstaged/discard them — this task is about validating the log
mechanism, not publishing new event data.
