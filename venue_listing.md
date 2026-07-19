# San Diego Venue Listing

Source: `venue_listing.txt`

**Scraper** column key:
- ✅ Built — a scraper/generator exists in `/scraper` and feeds the events page
- 🟡 JS-only — events are rendered client-side (needs a headless browser)
- 🔗 Link-out — large arena on Ticketmaster/Live Nation (anti-bot, not
  local-club programming); not scraped, but surfaced as a pill on the page that
  links straight to its ticketing site
- ⚪ No events posted — site reachable but its events page is empty
- 🕐 Deferred — scrapeable in principle but needs a net-new scraper (or a retry); parked for a later pass
- 🔴 Unreachable — domain does not resolve / refuses connections

See `scraper/README.md` for details.

## Primary Venues

| # | Venue | Official Website | Scraper |
|---|-------|------------------|---------|
| 1 | Casbah | https://www.casbahmusic.com | ✅ Built |
| 2 | McGuffie's Live | https://mcguffieslive.com | ✅ Built |
| 3 | Deano's Pub | https://deanospub.com/ | ✅ Built (flyer) |
| 4 | Camel's Bar | camelsbarandgrill.com | ✅ Built (recurring) |
| 5 | Snapdragon Stadium | https://snapdragonstadium.com | 🔗 Link-out (Ticketmaster) |
| 6 | The Holding Company | https://www.theholdingcompanyob.com | ✅ Built |
| 7 | Ken Club (Kensington Club) | https://www.kensingtonclub1935.com/ | ✅ Built |
| 8 | Queen Bee's | https://www.queenbeessd.com | ✅ Built (recurring) |
| 9 | Black Cat Bar | https://blackcatbar.wordpress.com | ✅ Built (flyer) |
| 10 | Brick By Brick | https://www.brickbybrick.com | ✅ Built |
| 11 | Soda Bar | https://sodabarmusic.com | ✅ Built (DICE) |
| 12 | Music Box | https://musicboxsd.com | ✅ Built |
| 13 | Banshee Bar | https://thebansheebar.com/ | ✅ Built (DICE) |
| 14 | Belly Up | https://bellyup.com | ✅ Built |
| 15 | North Island Credit Union Amphitheatre | https://www.livenation.com/venue/KovZpa2WZe/north-island-credit-union-amphitheatre-events | 🔗 Link-out (Ticketmaster) |
| 16 | House of Blues | https://www.houseofblues.com/sandiego | ✅ Built |
| 17 | Voodoo Room, House of Blues | https://www.houseofblues.com/sandiego | ✅ Built (with #16) |
| 18 | Grand Ole BBQ, Flinn Springs | https://grandolebbq.com | ⚪ No events posted |
| 19 | The Jazz Lounge | https://www.thejazzlounge.live | ⚪ Broken calendar embed |
| 20 | Winston's | https://winstonsob.com | ✅ Built |
| 21 | Tower Bar | https://www.thetowerbar.com | ✅ Built |
| 22 | The Observatory North Park | https://www.observatorysd.com | ✅ Built |
| 23 | The Sound | https://thesoundsd.com | ✅ Built |
| 24 | SOMA (Mainstage + Sidestage) | https://www.somasandiego.com | ✅ Built |
| 25 | Whistle Stop | https://www.whistlestopbar.com | ✅ Built |
| 26 | Petco Park | https://www.mlb.com/padres/ballpark | 🔗 Link-out (Ticketmaster) |

## Secondary Venues

**Plan:** venues that matched an existing helper (Tribe API, the shared Casbah
Presents feed) are built. 🕐 Deferred rows need a net-new scraper — JS-rendered
sites, custom CMSs, or ticketing platforms we don't parse yet — and will be
tackled in a later pass. 🔴 rows didn't resolve on the last probe (retry, the
domain may be wrong or dead). Duplicate rows of the same website (Panama 66,
Blind Lady, SeaWorld, Margaritaville, Athenaeum) only need one scraper each.

| # | Venue | Official Website | Scraper |
|---|-------|------------------|---------|
| 27 | Lou Lou's Jungle Room, Lafayette Hotel | https://www.thelafayette.com | ✅ Built (Casbah feed) |
| 28 | Dizzy's | https://dizzysjazz.com | 🕐 Deferred (net-new) |
| 29 | EQ | https://eqsd.com | 🕐 Deferred (net-new) |
| 30 | Rich's | https://richssandiego.com | ⚪ Tribe API live, 0 events |
| 31 | The Brass Rail | https://www.thebrassrailsd.com | 🕐 Deferred (net-new) |
| 32 | California Center for the Arts, Escondido | https://artcenter.org | ✅ Built (Tribe) |
| 33 | Athenaeum Art Center \| Barrio Logan | https://www.ljathenaeum.org | 🕐 Deferred (net-new) |
| 34 | Humphrey's Backstage Live | https://www.humphreysbackstagelive.com | ✅ Built (Tribe) |
| 35 | Moonlight Amphitheatre | https://moonlightstage.com | 🕐 Deferred (net-new) |
| 36 | The Old Globe | https://www.theoldglobe.org | 🕐 Deferred (net-new) |
| 37 | New Village Arts | https://newvillagearts.org | ✅ Built (Tribe) |
| 38 | Cygnet Theatre \| The Joan at Liberty Station | https://cygnettheatre.org | 🕐 Deferred (net-new) |
| 39 | Lamb's Players Theatre | https://lambsplayers.org | 🕐 Deferred (net-new) |
| 40 | North Coast Repertory Theatre | https://northcoastrep.org | 🕐 Deferred (net-new) |
| 41 | Aquarius Bar & Grille | https://www.aquariusbargrille.com | 🕐 Deferred (net-new) |
| 42 | Mr. Peabody's | https://mrpeabodys.net | 🔴 Unreachable |
| 43 | Cannonball | https://www.cannonballsd.com | 🕐 Deferred (net-new) |
| 44 | Tio Leo's | https://tioleos.com | 🕐 Deferred (net-new) |
| 45 | Pour House | https://www.pourhousesd.com | 🕐 Deferred (net-new) |
| 46 | Pechanga Arena San Diego | https://pechangaarenasd.com | ✅ Built (Tribe) |
| 47 | Mixed Grounds Coffee | https://www.mixedgroundscoffee.com | 🔴 Unreachable |
| 48 | Coyote Bar & Grill, Carlsbad | https://www.coyotecarlsbad.com | 🕐 Deferred (net-new) |
| 49 | SPIN | https://spinnightclub.com | 🕐 Deferred (net-new) |
| 50 | Grand Lobby, Westgate Hotel | https://www.westgatehotel.com | 🕐 Deferred (net-new) |
| 51 | Aztec Brewing Company, Vista | https://aztecbrewing.com | 🕐 Deferred (net-new) |
| 52 | Luau Bar | https://www.luaubar.com | 🔴 Unreachable |
| 53 | 710 Beach Club | https://www.710bc.com | 🕐 Deferred (net-new) |
| 54 | 535 Robinson (Pride Block Party site) | Special event location — no official venue website | ⚪ No venue website |
| 55 | Balboa Theatre | https://www.sandiegotheatres.org | 🕐 Deferred (net-new) |
| 56 | The Rady Shell at Jacobs Park | https://www.theshell.org | 🕐 Deferred (net-new) |
| 57 | Panama 66 | https://www.panama66.com | 🕐 Deferred (net-new) |
| 58 | Fast Times | https://www.fasttimessd.com | 🕐 Deferred (net-new) |
| 59 | Riviera Supper Club | https://www.rivierasupperclub.com | 🕐 Deferred (net-new) |
| 60 | Moonshine Flats | https://moonshineflats.com | 🕐 Deferred (net-new) |
| 61 | San Diego Natural History Museum | https://www.sdnhm.org | 🕐 Deferred (net-new) |
| 62 | La Jolla Playhouse | https://lajollaplayhouse.org | 🕐 Deferred (net-new) |
| 63 | Oceanside Theatre Company at The Brooks | https://oceansidetheatre.org | 🕐 Deferred (net-new) |
| 64 | Adams Avenue Theater | https://adamsavenuetheater.com | 🔴 Unreachable |
| 65 | The Rabbit Hole | https://www.therabbitholesd.com | 🔴 Unreachable |
| 66 | 5 o'Clock Somewhere Bar (Margaritaville Hotel) | https://www.margaritavilleresorts.com/margaritaville-hotel-san-diego-gaslamp-quarter | 🕐 Deferred (net-new) |
| 67 | LandShark Bar & Grill (Margaritaville Hotel) | https://www.margaritavilleresorts.com/margaritaville-hotel-san-diego-gaslamp-quarter | 🕐 Deferred (net-new) |
| 68 | Renegade Country | https://renegade.country | 🔴 Unreachable |
| 69 | Lobby Bar, Sycuan Casino Resort | https://www.sycuan.com | 🕐 Deferred (net-new) |
| 70 | Quartyard | https://www.quartyardsd.com | ✅ Built (Casbah feed) |
| 71 | Pop Up Winona | https://popupwinona.com | 🔴 Unreachable |
| 72 | Blind Lady Ale House | https://www.blindladyalehouse.com | 🕐 Deferred (net-new) |
| 73 | Mo's | https://mosuniverse.com | 🕐 Deferred (net-new) |
| 74 | Moonshine Beach | https://moonshinebeachsd.com | 🕐 Deferred (net-new) |
| 75 | Del Mar Racetrack | https://web.dmtc.com | 🔴 Unreachable |
| 76 | L'Auberge Del Mar | https://www.laubergedelmar.com | 🕐 Deferred (net-new) |
| 77 | University Ave & Richmond Ave | — | ⚪ No venue website |
| 78 | Marston Point, Balboa Park | https://www.balboapark.org | 🕐 Deferred (Tribe=219 park-wide; needs curation) |
| 79 | Humphrey's Concerts By The Bay | https://www.humphreysconcerts.com | ✅ Built (Casbah feed) |
| 80 | Platform 34 | https://www.platform34sd.com | 🔴 Unreachable |
| 81 | Worldbeat Center | https://www.worldbeatcenter.org | ✅ Built (Tribe) |
| 82 | Bayfront Amphitheatre, SeaWorld | https://seaworld.com/san-diego | 🕐 Deferred (net-new) |
| 83 | The Heart OB | https://www.theheartob.com | 🕐 Deferred (Wix JS) |
| 84 | Ramona Mainstage | https://ramonamainstage.com | 🕐 Deferred (net-new) |
| 85 | Bates Nut Farm | https://batesnutfarm.biz | 🕐 Deferred (net-new) |
| 86 | Museum of Making Music | https://www.museumofmakingmusic.org | 🕐 Deferred (net-new) |
| 87 | Frontwave Arena | https://www.frontwavearena.com | 🕐 Deferred (net-new) |
| 88 | Kate Sessions Park | https://www.sandiego.gov/park-and-recreation/parks/regional/balboa/kate-sessions | 🕐 Deferred (net-new) |
| 89 | Southwestern College, DeVore Stadium | https://swcathletics.com | 🔴 Unreachable |
| 90 | Orca Stadium, SeaWorld | https://seaworld.com/san-diego | 🕐 Deferred (net-new) |
| 91 | Fit Social, Belmont Park | https://fitathletic.com | 🕐 Deferred (net-new) |
| 92 | La Jolla Athenaeum Music & Arts Library | https://www.ljathenaeum.org | 🕐 Deferred (net-new) |
| 93 | Spreckels Organ Pavilion | https://spreckelsorgan.org | 🕐 Deferred (net-new) |
| 94 | Neon Moon | https://www.neonmoonsd.com | 🕐 Deferred (net-new) |
| 95 | Epstein Family Amphitheater | https://amphitheater.ucsd.edu | ✅ Built (Tribe) |
| 96 | Cal Coast Credit Union Open Air Theatre, SDSU | https://as.sdsu.edu/calcoast | 🕐 Deferred (net-new) |
| 97 | Corazon Del Barrio | https://corazondelbarrio.org | 🕐 Deferred (Wix JS) |
| 98 | Bancroft Bar | https://www.bancroftbar.com | 🕐 Deferred (net-new) |
| 99 | Fall Brewing | https://fallbrewingcompany.com | 🕐 Deferred (net-new) |
| 100 | Copley Auditorium, Panama 66 | https://www.panama66.com | 🕐 Deferred (net-new) |
| 101 | Blind Lady Ale House \| Live In The Hamm's Room | https://blindladyalehouse.com | 🕐 Deferred (net-new) |
| 102 | Southwestern College Performing Arts Center | https://www.swccd.edu/campus-life/performing-arts-center/index.aspx | 🕐 Deferred (net-new) |
| 103 | Hilton San Diego Gaslamp Quarter | https://www.hilton.com/en/hotels/sanhhhf-hilton-san-diego-gaslamp-quarter | 🕐 Deferred (net-new) |
| 104 | American Junkie | https://americanjunkiesd.com | 🕐 Deferred (net-new) |
