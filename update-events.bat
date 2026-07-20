@echo off
REM ============================================================
REM  Double-click to refresh all venue data.
REM  1. Re-runs every scraper/generator and rebuilds:
REM       - js/events-data.js   (list + calendar events, incl.
REM         "added" stamps that power the New filter)
REM       - data/events.json
REM       - data/*-flyer.*      (Deano's + Black Cat flyer images)
REM  2. Commits the refreshed data and pushes it to GitHub.
REM  Then just refresh the events page in your browser.
REM ============================================================

cd /d "%~dp0scraper"

echo Updating San Diego Live events data...
echo.

REM Use the py launcher if present, otherwise fall back to python.
where py >nul 2>nul
if %errorlevel%==0 (
    py build_events_data.py
) else (
    python build_events_data.py
)

if not %errorlevel%==0 goto :buildfail

echo.
echo Committing and pushing to GitHub...
cd /d "%~dp0"
git add -A
git diff --cached --quiet
if %errorlevel%==0 goto :nochanges

git commit -m "Refresh event data (%date% %time:~0,5%)" -m "Automated data refresh via update-events.bat" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
if not %errorlevel%==0 goto :gitfail
git push origin main
if not %errorlevel%==0 goto :pushfail

echo.
echo Done. Data refreshed, committed, and pushed.
echo Refresh the events page in your browser to see the changes.
goto :end

:nochanges
echo.
echo Done. Data is unchanged since the last run - nothing to commit.
goto :end

:buildfail
echo.
echo The scrape failed - see the messages above. Nothing was committed.
goto :end

:gitfail
echo.
echo Data was refreshed but the git commit failed - see the messages above.
goto :end

:pushfail
echo.
echo Data was committed locally but the push failed (offline?).
echo Run "git push" later, or just double-click this file again.
goto :end

:end
echo.
pause
