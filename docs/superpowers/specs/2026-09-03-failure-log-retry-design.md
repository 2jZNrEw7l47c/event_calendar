# Failure logging & retry for the scrape run

Date: 2026-09-03

## Problem

`scraper/build_events_data.py` currently swallows per-venue scraper failures
silently (`print("!! %s failed: %s" % (label, exc))`) and moves on. There's
no record of which venues failed, how often, or with what error, so a venue
whose site changed its markup can silently produce zero events indefinitely
without anyone noticing.

## Goals

- Track every failure (venue/flyer scraper + error code/message) in an Excel
  log so failures are visible and inspectable between runs.
- Automatically retry failures once per run; drop them from the log the
  moment a retry succeeds.
- Surface venues that have failed 5 runs in a row (no success in between) as
  needing a script rewrite, since that's a strong signal the source site
  changed.
- Keep the existing terminal output shape (`Updating {title}..` as it goes)
  and add the two closing lines the user specified.

## Scope

Applies to every entry in `SCRAPERS` (44 venues) and `FLYER_SCRAPERS` (Deano's
Pub, Black Cat) in `scraper/build_events_data.py` — i.e. everything that's
already individually try/excepted in `main()` today. One "item" = one venue's
display label.

Out of scope: `update-events.bat`'s commit/push logic is unchanged. The build
script still exits 0 and pushes whatever data it produced even when some
venues remain failed — a broken venue shouldn't block everyone else's fresh
data from going live (confirmed with user).

## Architecture

### New module: `scraper/failure_log.py`

A thin wrapper around an `openpyxl` workbook at `scraper/failure_log.xlsx`,
with two sheets:

- **Failures** — one row per venue currently failing (after this run's
  retry): `Venue | Error Code | Error Message | Consecutive Fails | Last Failed`.
- **Frequent Failures** — same columns, filtered to rows where
  `Consecutive Fails >= 5`. Purely a filtered view recomputed each save; not
  separately maintained state.

Functions:

- `load(path) -> dict[str, dict]` — reads the `Failures` sheet into
  `{venue: {"error_code", "error_message", "consecutive_fails", "last_failed"}}`.
  Returns `{}` if the file doesn't exist yet (first run).
- `record_failure(log, venue, error_code, error_message, now)` — upserts the
  venue's entry, incrementing `consecutive_fails` by 1 (starting at 1 if the
  venue wasn't already in the log), and updating error code/message/timestamp.
- `record_success(log, venue)` — deletes the venue's entry if present (streak
  resets to 0 — a fresh future failure starts the count over at 1).
- `save(path, log)` — writes both sheets from the current `log` dict,
  overwriting the file.

"Consecutive" is run-to-run, not attempt-to-attempt: one run that ultimately
fails (initial attempt + retry both fail) counts as **one** increment, not two.
A run that succeeds (on the initial attempt or the retry) clears the streak.

### `error_code` / `error_message` capture

A small helper (in `failure_log.py` or inline in `build_events_data.py`):

```python
def classify(exc):
    if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
        return "HTTP %d" % exc.response.status_code, str(exc)
    return type(exc).__name__, str(exc)
```

`error_message` is stored as-is (Excel cells handle long strings fine; no
truncation needed at this scale).

### `build_events_data.py` changes

`main()` currently loops `SCRAPERS` once, catching exceptions inline. New
flow:

1. `log = failure_log.load(LOG_PATH)` at the top of `main()`.
2. **First pass** over `SCRAPERS` + `FLYER_SCRAPERS`: print
   `Updating {label}..`, call the scraper. On success, keep the result and
   (if the venue was previously failing) mark it for `record_success`. On
   exception, classify the error and hold `(label, fn, error_code, error_message)`
   in a `pending` list — don't touch the log yet.
3. **Retry pass** over `pending`: print `Retrying {label}..`, call the
   scraper again.
   - Succeeds → use the result as if it had succeeded the first time;
     `record_success(log, label)`.
   - Fails again → `record_failure(log, label, error_code, error_message, now)`;
     venue's events stay empty for this run (same as current behavior).
4. `failure_log.save(LOG_PATH, log)`.
5. For any venue whose `consecutive_fails` just reached exactly 5 this run
   (i.e. crossed the threshold on this save, not one that was already at 5+
   from a prior run), print:
   `!! {label} has failed 5+ runs in a row - script may need a rewrite`
6. After the existing per-venue summary printout, print `failures:` on its
   own line, then each still-failing venue's label on its own line below it:
   ```
   failures:
   <label 1>
   <label 2>
   ```
   (or `failures: none` if the log is empty after this run's retry).
7. Finally print:
   `the updates are available here: https://2jznrew7l47c.github.io/event_calendar/`

Flyer scrapers currently return an `info` dict (or `None`) rather than a list
of events; they fold into the same first-pass/retry/log machinery, just with
their own result-handling branch (as `main()` already has two separate loops
for events vs. flyers — the pending-retry logic is applied to both, but the
loops themselves stay distinct since their result shapes differ).

### `requirements.txt`

Add `openpyxl>=3.1`.

## Error handling

- If `scraper/failure_log.xlsx` is missing, corrupt, or unreadable, `load()`
  treats it as an empty log (matches "first build with tracking" precedent
  already used for `_stamp_added`'s `events.json` handling) rather than
  crashing the whole build.
- `save()` failures (e.g. file locked because it's open in Excel) should
  print a warning and not abort the rest of the build — the events data is
  more important than the log.

## Testing

- Unit-test `failure_log.py`'s `load`/`record_failure`/`record_success`/`save`
  round-trip against a temp `.xlsx` path (no network needed).
- Manually verify `main()`'s new flow by temporarily forcing one scraper to
  raise, confirming: it retries, logs on second failure, appears in
  `failures:` output, and disappears from the log on a run where it's made to
  succeed.
- No existing test suite in the repo today; this introduces the first tests
  under `scraper/`. Keep them isolated (`scraper/test_failure_log.py`,
  runnable via `python -m unittest` or `pytest` if available) — not wired
  into `update-events.bat` since that's meant for non-technical double-click
  use.
