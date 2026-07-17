# Venue scrapers

Pull live event schedules straight from each venue's own website and generate
the data file the events page loads.

## What it does

- `scrape_casbah.py` — Casbah (casbahmusic.com). WordPress + See Tickets plugin;
  events are in the server-rendered HTML. Filters the shared "Casbah Presents"
  feed down to the Casbah room only.
- `scrape_mcguffies.py` — McGuffie's Live (mcguffieslive.com/shows). GoDaddy
  Website Builder; events are laid out as "Menu" items with `data-aid`
  attributes. Times are hand-typed, so they're parsed best-effort and the
  original wording is kept in each event's description.
- `scrape_camels.py` — Camel's Bar (camelsbarandgrill.com). **No online schedule**
  — just a text description of two standing jams. Not a scraper: it expands
  those recurrence rules ("every Tuesday", "every 2nd Sunday") into concrete
  dated occurrences over a rolling 6-month window. Edit the `RULES` list if the
  venue's standing schedule changes.
- `scrape_deanos.py` — Deano's Pub (deanospub.com). **Image-only schedule.**
  Deano's posts its week as a single flyer graphic under the "This week's
  events!" section, with no text to parse. Rather than OCR the artwork (brittle
  on stylized fonts), we download the current flyer and the page shows it in a
  dialog behind a "Deano's Pub" button. Discovery is positional — the first
  hosted image after the "This week's events" heading — so it keeps working when
  they swap in a new flyer (the filename is a content hash that changes each
  update). The image is saved to `../data/deanos-flyer.<ext>`.
- `common.py` — shared HTTP headers and date/time parsing (incl. year inference,
  since neither text site prints a year).
- `build_events_data.py` — runs every scraper, merges + sorts the results, and
  writes:
  - `../js/events-data.js` — consumed by the page
    (`window.CATEGORIES`, `window.EVENTS`, `window.FLYERS`)
  - `../data/events.json` — same data as plain JSON, for reference/other tools

No LLM and no headless browser are needed — the text sites serve their event
data in raw HTML, and Deano's flyer is shown as-is rather than parsed.

### Text venues vs. flyer venues

- **Text venues** (Casbah, McGuffie's) expose `scrape(today) -> list[event dict]`
  and are listed in `SCRAPERS`. Their events show up in the list/calendar.
- **Flyer venues** (Deano's) expose `scrape(today) -> flyer metadata dict` and
  are listed in `FLYER_SCRAPERS`. They surface as a button that opens the flyer
  image in a dialog (see `window.FLYERS`).

## Usage

```bash
pip install -r requirements.txt          # first time only
python build_events_data.py              # rebuild js/events-data.js from live sites
```

Then reload the events page. Run the individual scrapers to spot-check one
venue:

```bash
python scrape_casbah.py
python scrape_mcguffies.py
```

## Adding a venue

1. Write `scrape_<venue>.py` exposing `scrape(today) -> list[event dict]`.
2. Add it to the `SCRAPERS` list in `build_events_data.py` with a category key
   and label.
3. Add a `--cat-<key>` color in `../css/style.css` (see `.cat-casbah`).

Each event dict uses these fields:

| field | notes |
|-------|-------|
| `id` | stable unique string |
| `title` | headliner / act |
| `date` | `YYYY-MM-DD` |
| `time` | 24h `HH:MM` (used for ordering + display) |
| `venue` | display name |
| `category` | venue key (drives filter pill + color) |
| `price` | free-text as listed |
| `description` | genre / notes / original listing text |
| `url` | ticket link, or `null` |

## Rolling back to the sample data

The original hand-written demo events are archived at
`../archive/dummy-events.js`. To restore them, copy that file's contents over
`../js/events-data.js`.

## Caveats

- **Year inference:** listings without a year are assumed to be the nearest
  upcoming occurrence (dates >14 days past roll to next year).
- **McGuffie's times** are approximate — a range like `9:45-2am` becomes a
  single start time (9:45 pm). Always confirm on the venue page.
- These parse each site's current HTML structure. If a venue redesigns its site,
  its scraper will need updating (the page falls back to an empty list rather
  than breaking).
