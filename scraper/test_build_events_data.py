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
                       "consecutive_fails": 2, "last_failed": "2026-09-02 10:00"}}
    newly_frequent = []
    bed._run_with_retry([("Casbah", always_fails)], TODAY, NOW, log, newly_frequent)
    assert log["Casbah"]["consecutive_fails"] == 3
    assert newly_frequent == ["Casbah"]

    # A second run that also fails both attempts must not re-flag it.
    newly_frequent2 = []
    bed._run_with_retry([("Casbah", always_fails)], TODAY, NOW, log, newly_frequent2)
    assert log["Casbah"]["consecutive_fails"] == 4
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


# ---------- is_empty (0-events-found) behavior ----------

def _not_empty(result):
    return not result


def test_empty_result_on_first_try_is_retried_and_succeeds(capsys):
    calls = {"n": 0}

    def flaky(today):
        calls["n"] += 1
        return [] if calls["n"] == 1 else ["event"]

    log = {}
    newly_frequent = []
    results = bed._run_with_retry([("Casbah", flaky)], TODAY, NOW, log, newly_frequent,
                                   is_empty=_not_empty)

    assert results == {"Casbah": ["event"]}
    assert log == {}
    out = capsys.readouterr().out
    assert "Updating Casbah.." in out
    assert "Retrying Casbah.." in out


def test_empty_result_both_times_is_logged_as_failure(capsys):
    def always_empty(today):
        return []

    log = {}
    newly_frequent = []
    results = bed._run_with_retry([("Casbah", always_empty)], TODAY, NOW, log, newly_frequent,
                                   is_empty=_not_empty)

    assert results == {"Casbah": None}
    assert log["Casbah"]["consecutive_fails"] == 1
    assert log["Casbah"]["error_code"] == "NoEventsFound"
    assert log["Casbah"]["last_failed"] == NOW
    out = capsys.readouterr().out
    assert "!! Casbah failed: scraper returned 0 events" in out


def test_empty_result_failures_also_count_toward_frequent_threshold():
    def always_empty(today):
        return []

    log = {"Casbah": {"error_code": "NoEventsFound", "error_message": "scraper returned 0 events",
                       "consecutive_fails": 2, "last_failed": "2026-09-02 10:00"}}
    newly_frequent = []
    bed._run_with_retry([("Casbah", always_empty)], TODAY, NOW, log, newly_frequent,
                         is_empty=_not_empty)

    assert log["Casbah"]["consecutive_fails"] == 3
    assert newly_frequent == ["Casbah"]


def test_is_empty_does_not_fire_on_a_normal_successful_result(capsys):
    def ok(today):
        return ["event"]

    log = {}
    newly_frequent = []
    results = bed._run_with_retry([("Casbah", ok)], TODAY, NOW, log, newly_frequent,
                                   is_empty=_not_empty)

    assert results == {"Casbah": ["event"]}
    assert log == {}
    out = capsys.readouterr().out
    assert "Retrying" not in out


def test_is_empty_exception_is_contained_like_a_scraper_exception(capsys):
    # A badly-behaved is_empty predicate must not crash the whole run — it's
    # contained per-item exactly like an exception from fn() itself.
    calls = {"n": 0}

    def ok(today):
        calls["n"] += 1
        return ["event"]

    def bad_is_empty(result):
        if calls["n"] == 1:
            raise TypeError("predicate blew up")
        return not result

    log = {}
    newly_frequent = []
    results = bed._run_with_retry([("Casbah", ok)], TODAY, NOW, log, newly_frequent,
                                   is_empty=bad_is_empty)

    assert results == {"Casbah": ["event"]}
    assert log == {}
    out = capsys.readouterr().out
    assert "Retrying Casbah.." in out


def test_default_is_empty_never_treats_a_successful_none_as_failure(capsys):
    # Flyer scrapers return None on success (no flyer posted this week) —
    # without an explicit is_empty, that must not be retried or logged.
    def returns_none(today):
        return None

    log = {}
    newly_frequent = []
    results = bed._run_with_retry([("Deano's Pub", returns_none)], TODAY, NOW, log, newly_frequent)

    assert results == {"Deano's Pub": None}
    assert log == {}
    out = capsys.readouterr().out
    assert "Retrying" not in out
