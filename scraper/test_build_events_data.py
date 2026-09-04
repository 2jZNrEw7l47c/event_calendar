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


# ---------- "New since" marker ----------

def test_new_since_is_this_run_when_it_added_events():
    events = [{"added": "2026-09-03 10:00"}, {"added": "2026-09-04 07:44"}]
    assert bed._new_since(events, "2026-09-04 07:44", 1) == "2026-09-04 07:44"


def test_new_since_holds_the_last_run_that_added_something():
    # A re-run that adds nothing must not blank out the New filter — it stays
    # pointed at the most recent run that actually brought events in.
    events = [{"added": "2026-08-08 11:30"}, {"added": "2026-09-03 16:18"}]
    assert bed._new_since(events, "2026-09-04 07:44", 0) == "2026-09-03 16:18"


def test_new_since_is_none_when_nothing_has_ever_been_stamped():
    events = [{"added": None}, {"added": None}]
    assert bed._new_since(events, "2026-09-04 07:44", 0) is None


def test_new_since_ignores_unstamped_events_when_picking_the_latest():
    events = [{"added": None}, {"added": "2026-09-03 16:18"}, {"added": None}]
    assert bed._new_since(events, "2026-09-04 07:44", 0) == "2026-09-03 16:18"


# ---------- index.html cache-buster ----------

def test_cache_token_is_compact_and_sortable():
    assert bed._cache_token("2026-09-04 07:32") == "20260904-0732"


def _index_with(tag, tmp_path):
    path = tmp_path / "index.html"
    path.write_text(
        '<html><body>\n'
        '  <script src="js/events-data.js%s"></script>\n'
        '  <script src="js/app.js?v=14"></script>\n'
        '</body></html>\n' % tag, encoding="utf-8")
    return str(path)


def test_stamp_index_html_replaces_existing_version(tmp_path):
    path = _index_with("?v=13", tmp_path)

    assert bed._stamp_index_html("2026-09-04 07:32", path) is True

    html = open(path, encoding="utf-8").read()
    assert 'src="js/events-data.js?v=20260904-0732"' in html
    assert "?v=13" not in html
    # Hand-versioned assets are left alone.
    assert 'src="js/app.js?v=14"' in html


def test_stamp_index_html_adds_version_when_missing(tmp_path):
    path = _index_with("", tmp_path)

    assert bed._stamp_index_html("2026-09-04 07:32", path) is True

    html = open(path, encoding="utf-8").read()
    assert 'src="js/events-data.js?v=20260904-0732"' in html


def test_stamp_index_html_is_a_noop_when_token_unchanged(tmp_path):
    path = _index_with("?v=20260904-0732", tmp_path)

    # Same stamp -> nothing rewritten, so re-running a build doesn't churn
    # index.html (and git) for no reason.
    assert bed._stamp_index_html("2026-09-04 07:32", path) is False


def test_stamp_index_html_warns_and_continues_when_tag_absent(tmp_path, capsys):
    path = str(tmp_path / "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write("<html><body>no data script here</body></html>")

    assert bed._stamp_index_html("2026-09-04 07:32", path) is False
    assert "no events-data.js script tag" in capsys.readouterr().out


def test_stamp_index_html_warns_and_continues_when_file_missing(tmp_path, capsys):
    missing = str(tmp_path / "nope" / "index.html")

    assert bed._stamp_index_html("2026-09-04 07:32", missing) is False
    assert "could not read" in capsys.readouterr().out
