# Pulling Schedules Directly: Casbah & McGuffie's Live

Findings from inspecting each venue's live site on 2026-07-17. Goal: get each
venue's event schedule **directly from its own website**, ideally in a
structured, machine-readable way.

The two sites are at opposite ends of the difficulty spectrum.

---

## 1. Casbah — https://www.casbahmusic.com

**Verdict: Easy. Clean, server-rendered event markup you can scrape reliably.**

### What's behind it
- Platform: **WordPress 7.0.2**.
- Ticketing / event data: the **See Tickets** WordPress plugin (`V35.3.1b`).
  The plugin renders the full event list into the page HTML **server-side** —
  there is no client-side JSON/XHR call to intercept (the only network requests
  are the plugin's own CSS/JS assets). So the events are present in the raw HTML
  the moment the page loads.
- No JSON-LD, and the WordPress REST API (`/wp-json/`) is enabled but does **not**
  expose events as a post type — so the REST API is a dead end for schedules.
  It is **not** running The Events Calendar plugin (`/wp-json/tribe/...` 404s).

### How to get the schedule
Scrape the rendered HTML of the homepage (or `/calendar/`, which returns 200).
Each event is a repeating block with **stable, semantic CSS classes**:

- Container list: `div.seetickets-list-events`
- Per event: `div.seetickets-list-event-container`
- Inside each, content lives in `div.seetickets-list-event-content-container`:

| Field | Selector |
|-------|----------|
| Date | `p.event-date` — e.g. `"Sun Jan 10"` |
| Header/tagline | `p.event-header` — e.g. `"Record Release Show!"` |
| Headliners / title | `p.headliners` |
| Venue | `p.venue` — e.g. `"at Casbah"` |
| Door time | `span.see-doortime` — e.g. `"3:00PM"` |
| Show time | `span.see-showtime` — e.g. `"4:00PM"` |
| Ages | `span.ages` — e.g. `"21+"` |
| Price | `span.price` — e.g. `"$22.00"` |
| Genre | `p.genre` — e.g. `"R&B"` |
| Ticket link | `a.seetickets-buy-btn` → `wl.seetickets.us/event/.../<id>` |

**Important caveat:** the Casbah site is the hub for the whole "Casbah Presents"
family, so the feed **mixes multiple venues** (Casbah, Whistle Stop, Belly Up,
Soda Bar, House of Blues, Observatory, SOMA, Quartyard, etc.). Filter on the
`p.venue` field (`"at Casbah"`) to isolate the Casbah room itself. Several of
those other venues are also on your listing, so one scrape of this site actually
covers a good chunk of the list.

The See Tickets ticket URLs contain a stable numeric event id
(`.../699421?afflky=Casbah`), which makes a good dedup/primary key.

### Extraction sketch
Fetch the page, parse with any HTML parser (BeautifulSoup / Cheerio), loop over
`.seetickets-list-event-container`, read the fields above. No JS execution
needed — a plain HTTP GET returns the fully populated markup. Year is not in the
date string, so infer it (roll the year forward when the month is earlier than
"today").

---

## 2. McGuffie's Live — https://mcguffieslive.com

**Verdict: Hard. No structured data at all — the schedule is hand-typed prose.**

### What's behind it
- Platform: **GoDaddy Website Builder 8.0** (Websites + Marketing).
- **No** third-party ticketing platform, **no** JSON-LD, **no** events API,
  **no** per-event markup or data attributes.
- The schedule on `/shows` is a single **free-text block** a person types by
  hand. Example of the actual content:

  > JULY 2026
  > July 15th at 9:45-2am — NO COVER — KARAOKE NIGHT — Sign ups start at 9:30 — T-DOG HOSTING
  > July 16th at 8pm — $12 COVER — NICK HAMES (STEVIE RAY VAUGHAN TRIBUTE)
  > July 17th at 8pm — $10 COVER — 2 LIL 2 LATE / REVELATION 69 (ORIGINAL ROCK/COVERS)

- The `/presale-tickets` page is likewise just typed text (e.g. "Cosmic
  Convergence Tour — Sept 29, 7PM — Presale: $15 | Door: $20") with a generic
  "Buy Presale Tickets" button and no ticketing integration behind it.
- The `/shows` content is injected by GoDaddy's JS after load, so you must
  **render the page** (headless browser) before reading it — a plain HTTP GET of
  the HTML won't contain the text.

### How to get the schedule
There is no clean feed, so this requires **text parsing of the rendered page**:

1. Load `https://mcguffieslive.com/shows` in a headless browser (Playwright /
   Puppeteer); wait ~1–1.5s for the GoDaddy widget to populate.
2. Grab the events section's `innerText`.
3. Parse the free-form lines. The house pattern is fairly consistent:

   ```
   <Month> <Day>(th/st/nd) at <time>  —  <cover/price or "NO COVER">  —  <ACT(S)>  (<genre>)
   ```

   A regex can capture most of it, but because it's hand-written the format
   drifts (ranges like "9:45-2am", multiple acts, "open to public" notes,
   hosting credits). This is a genuinely good case for an **LLM parse** of the
   text block into structured JSON rather than brittle regex.

4. There is no year on individual lines — only a `JULY 2026` style month header
   to anchor from. Track the current month header while parsing.

### Reality check
Expect this one to break whenever they retype the block, and to need a
human/LLM in the loop. If you end up building an aggregator, McGuffie's is the
kind of venue where it may be less effort to re-enter events manually than to
maintain a scraper.

---

## Summary

| | Casbah | McGuffie's Live |
|---|--------|-----------------|
| Platform | WordPress + See Tickets plugin | GoDaddy Website Builder |
| Data shape | Structured HTML, semantic classes | Free-text prose |
| Rendered server-side? | Yes (plain GET works) | No (needs headless render) |
| Ticketing system | See Tickets (`wl.seetickets.us`) | None / manual |
| Stable event id? | Yes (See Tickets numeric id) | No |
| Extraction | HTML parse by CSS selector | Headless render + LLM/regex text parse |
| Effort | Low | High / brittle |
| Bonus | One scrape also covers Belly Up, Soda Bar, Whistle Stop, Observatory, SOMA, Quartyard, HOB | — |
