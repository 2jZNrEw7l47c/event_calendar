"""Probe: how many JSON-LD events does each venue yield? Planning aid; deletable."""
import concurrent.futures as cf
import ld_events

VENUES = [
    ("Snapdragon Stadium", "https://snapdragonstadium.com"),
    ("The Holding Company", "https://www.theholdingcompanyob.com"),
    ("Ken Club", "https://www.kenclubsd.com"),
    ("Queen Bee's", "https://queenbeessd.com"),
    ("Black Cat Bar", "https://www.blackcatsd.com"),
    ("Brick By Brick", "https://www.brickbybrick.com"),
    ("Soda Bar", "https://www.sodabarmusic.com"),
    ("Music Box", "https://musicboxsd.com"),
    ("Banshee Bar", "https://www.bansheebar.com"),
    ("Belly Up", "https://bellyup.com"),
    ("House of Blues", "https://www.houseofblues.com/sandiego"),
    ("Grand Ole BBQ", "https://grandolebbq.com"),
    ("The Jazz Lounge", "https://www.thejazzlounge.live"),
    ("Winston's", "https://winstonsob.com"),
    ("Tower Bar", "https://www.thetowerbar.com"),
    ("Observatory North Park", "https://www.observatorysd.com"),
    ("The Sound", "https://thesoundsd.com"),
    ("SOMA Sidestage", "https://www.somasandiego.com"),
    ("Whistle Stop", "https://www.whistlestopbar.com"),
]


def probe(item):
    name, url = item
    try:
        evs = ld_events.scrape_ld(url, name, "x")
        sample = "; ".join("%s %s" % (e["date"], e["title"][:22]) for e in evs[:2])
        return "%-24s %3d  %s" % (name, len(evs), sample)
    except Exception as e:
        return "%-24s ERR %s" % (name, str(e)[:50])


with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for line in ex.map(probe, VENUES):
        print(line)
