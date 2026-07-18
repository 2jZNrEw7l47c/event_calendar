# San Diego Live

A clean, static events page for San Diego live-music venues, with a **list view**
and a **month calendar view**, filterable by venue. Event data is pulled directly
from each venue's own website by a small set of Python scrapers.

No framework, no build step for the page itself — just HTML, CSS, and vanilla JS.
The only "build" is running the scrapers to refresh the data file the page loads.

## Quick start

Open the page:

```bash
# from the project root — any static server works
python -m http.server 4173
# then visit http://localhost:4173
```

Refresh the event data:

- **Windows:** double-click `update-events.bat`
- **Any OS:**
  ```bash
  pip install -r scraper/requirements.txt   # first time only
  python scraper/build_events_data.py
  ```
  Then reload the page.

## How it works

The page (`index.html` + `css/style.css` + `js/app.js`) reads its data from
`js/events-data.js`, which exposes three globals:

- `window.CATEGORIES` — venue key → label (drives the filter pills + colors)
- `window.EVENTS` — the flat list of events (list + calendar)
- `window.FLYERS` — image-only venues shown via a button + dialog

That file is **generated** by `scraper/build_events_data.py`, which runs every
venue scraper, merges and sorts the results, and also writes `data/events.json`.

### Venues currently wired up

| Venue | Source | Approach |
|-------|--------|----------|
| Casbah | casbahmusic.com | Parses server-rendered See Tickets HTML; filtered to the Casbah room |
| McGuffie's Live | mcguffieslive.com | Parses GoDaddy "Menu" event items |
| Camel's Bar | (text description) | Expands recurring weekly/monthly jams into dated events |
| Deano's Pub | deanospub.com | Downloads the weekly flyer image; shown in a dialog (no OCR) |

No LLM and no headless browser are needed — the text sites serve their data in
raw HTML, and Deano's flyer is displayed as-is. See
[`scraper/README.md`](scraper/README.md) for per-venue details and how to add a
new venue. The full venue list and scraper status is in
[`venue_listing.md`](venue_listing.md).

## Project layout

```
index.html              # the page
css/style.css           # all styling
js/app.js               # list + calendar rendering, filters, dialogs
js/events-data.js       # GENERATED event data (do not edit by hand)
data/                   # events.json + downloaded flyer image
scraper/                # Python scrapers + build_events_data.py
archive/                # preserved original dummy data
update-events.bat       # double-click to refresh all data (Windows)
venue_listing.md        # master venue list + scraper build status
```

## Notes

- **List view starts at today** — nothing earlier is shown. The calendar keeps
  full history so you can page back.
- Neither text site prints a year, so the scrapers infer it (nearest upcoming
  occurrence).
- Refreshing requires an internet connection. If one venue's site is down, that
  venue is skipped and the rest still build.
