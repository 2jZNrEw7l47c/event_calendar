# San Diego Venue Listing

Source: `venue_listing.txt`

**Scraper** column key:
- ✅ Built — a scraper/generator exists in `/scraper` and feeds the events page
- 🟡 JS-only — events are rendered client-side (needs a headless browser)
- 🔗 Link-out — large arena on Ticketmaster/Live Nation (anti-bot, not
  local-club programming); not scraped, but surfaced as a pill on the page that
  links straight to its ticketing site
- ⚪ No events posted — site reachable but its events page is empty
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

| # | Venue | Official Website | Scraper |
|---|-------|------------------|---------|
| 27 | Lou Lou's Jungle Room, Lafayette Hotel | https://www.thelafayette.com | — |
| 28 | Dizzy's | https://dizzysjazz.com | — |
| 29 | EQ | https://eqsd.com | — |
| 30 | Rich's | https://richssandiego.com | — |
| 31 | The Brass Rail | https://www.thebrassrailsd.com | — |
| 32 | California Center for the Arts, Escondido | https://artcenter.org | — |
| 33 | Athenaeum Art Center \| Barrio Logan | https://www.ljathenaeum.org | — |
| 34 | Humphrey's Backstage Live | https://www.humphreysbackstagelive.com | — |
| 35 | Moonlight Amphitheatre | https://moonlightstage.com | — |
| 36 | The Old Globe | https://www.theoldglobe.org | — |
| 37 | New Village Arts | https://newvillagearts.org | — |
| 38 | Cygnet Theatre \| The Joan at Liberty Station | https://cygnettheatre.org | — |
| 39 | Lamb's Players Theatre | https://lambsplayers.org | — |
| 40 | North Coast Repertory Theatre | https://northcoastrep.org | — |
| 41 | Aquarius Bar & Grille | https://www.aquariusbargrille.com | — |
| 42 | Mr. Peabody's | https://mrpeabodys.net | — |
| 43 | Cannonball | https://www.cannonballsd.com | — |
| 44 | Tio Leo's | https://tioleos.com | — |
| 45 | Pour House | https://www.pourhousesd.com | — |
| 46 | Pechanga Arena San Diego | https://pechangaarenasd.com | — |
| 47 | Mixed Grounds Coffee | https://www.mixedgroundscoffee.com | — |
| 48 | Coyote Bar & Grill, Carlsbad | https://www.coyotecarlsbad.com | — |
| 49 | SPIN | https://spinnightclub.com | — |
| 50 | Grand Lobby, Westgate Hotel | https://www.westgatehotel.com | — |
| 51 | Aztec Brewing Company, Vista | https://aztecbrewing.com | — |
| 52 | Luau Bar | https://www.luaubar.com | — |
| 53 | 710 Beach Club | https://www.710bc.com | — |
| 54 | 535 Robinson (Pride Block Party site) | Special event location — no official venue website | — |
| 55 | Balboa Theatre | https://www.sandiegotheatres.org | — |
| 56 | The Rady Shell at Jacobs Park | https://www.theshell.org | — |
| 57 | Panama 66 | https://www.panama66.com | — |
| 58 | Fast Times | https://www.fasttimessd.com | — |
| 59 | Riviera Supper Club | https://www.rivierasupperclub.com | — |
| 60 | Moonshine Flats | https://moonshineflats.com | — |
| 61 | San Diego Natural History Museum | https://www.sdnhm.org | — |
| 62 | La Jolla Playhouse | https://lajollaplayhouse.org | — |
| 63 | Oceanside Theatre Company at The Brooks | https://oceansidetheatre.org | — |
| 64 | Adams Avenue Theater | https://adamsavenuetheater.com | — |
| 65 | The Rabbit Hole | https://www.therabbitholesd.com | — |
| 66 | 5 o'Clock Somewhere Bar (Margaritaville Hotel) | https://www.margaritavilleresorts.com/margaritaville-hotel-san-diego-gaslamp-quarter | — |
| 67 | LandShark Bar & Grill (Margaritaville Hotel) | https://www.margaritavilleresorts.com/margaritaville-hotel-san-diego-gaslamp-quarter | — |
| 68 | Renegade Country | https://renegade.country | — |
| 69 | Lobby Bar, Sycuan Casino Resort | https://www.sycuan.com | — |
| 70 | Quartyard | https://www.quartyardsd.com | — |
| 71 | Pop Up Winona | https://popupwinona.com | — |
| 72 | Blind Lady Ale House | https://www.blindladyalehouse.com | — |
| 73 | Mo's | https://mosuniverse.com | — |
| 74 | Moonshine Beach | https://moonshinebeachsd.com | — |
| 75 | Del Mar Racetrack | https://web.dmtc.com | — |
| 76 | L'Auberge Del Mar | https://www.laubergedelmar.com | — |
| 77 | University Ave & Richmond Ave | — | — |
| 78 | Marston Point, Balboa Park | https://www.balboapark.org | — |
| 79 | Humphrey's Concerts By The Bay | https://www.humphreysconcerts.com | — |
| 80 | Platform 34 | https://www.platform34sd.com | — |
| 81 | Worldbeat Center | https://www.worldbeatcenter.org | — |
| 82 | Bayfront Amphitheatre, SeaWorld | https://seaworld.com/san-diego | — |
| 83 | The Heart OB | https://www.theheartob.com | — |
| 84 | Ramona Mainstage | https://ramonamainstage.com | — |
| 85 | Bates Nut Farm | https://batesnutfarm.biz | — |
| 86 | Museum of Making Music | https://www.museumofmakingmusic.org | — |
| 87 | Frontwave Arena | https://www.frontwavearena.com | — |
| 88 | Kate Sessions Park | https://www.sandiego.gov/park-and-recreation/parks/regional/balboa/kate-sessions | — |
| 89 | Southwestern College, DeVore Stadium | https://swcathletics.com | — |
| 90 | Orca Stadium, SeaWorld | https://seaworld.com/san-diego | — |
| 91 | Fit Social, Belmont Park | https://fitathletic.com | — |
| 92 | La Jolla Athenaeum Music & Arts Library | https://www.ljathenaeum.org | — |
| 93 | Spreckels Organ Pavilion | https://spreckelsorgan.org | — |
| 94 | Neon Moon | https://www.neonmoonsd.com | — |
| 95 | Epstein Family Amphitheater | https://amphitheater.ucsd.edu | — |
| 96 | Cal Coast Credit Union Open Air Theatre, SDSU | https://as.sdsu.edu/calcoast | — |
| 97 | Corazon Del Barrio | https://corazondelbarrio.org | — |
| 98 | Bancroft Bar | https://www.bancroftbar.com | — |
| 99 | Fall Brewing | https://fallbrewingcompany.com | — |
| 100 | Copley Auditorium, Panama 66 | https://www.panama66.com | — |
| 101 | Blind Lady Ale House \| Live In The Hamm's Room | https://blindladyalehouse.com | — |
| 102 | Southwestern College Performing Arts Center | https://www.swccd.edu/campus-life/performing-arts-center/index.aspx | — |
| 103 | Hilton San Diego Gaslamp Quarter | https://www.hilton.com/en/hotels/sanhhhf-hilton-san-diego-gaslamp-quarter | — |
| 104 | American Junkie | https://americanjunkiesd.com | — |
