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
