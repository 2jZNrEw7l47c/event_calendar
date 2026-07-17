@echo off
REM ============================================================
REM  Double-click to refresh all venue data.
REM  Re-runs every scraper/generator and rebuilds:
REM    - js/events-data.js   (list + calendar events)
REM    - data/events.json
REM    - data/deanos-flyer.* (Deano's weekly flyer image)
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

set EXITCODE=%errorlevel%
echo.
if %EXITCODE%==0 (
    echo Done. Refresh the events page in your browser to see the changes.
) else (
    echo Something went wrong ^(exit code %EXITCODE%^). See the messages above.
)

echo.
pause
