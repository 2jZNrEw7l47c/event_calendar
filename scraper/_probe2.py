"""Second-round probes for non-JSON-LD venues. Planning aid; deletable."""
import re, json, requests
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}

def get(url, **kw):
    return requests.get(url, headers=UA, timeout=30, **kw)

print("=== Tribe (The Events Calendar) REST API ===")
for name, base in [("Holding Company", "https://www.theholdingcompanyob.com"),
                   ("Whistle Stop", "https://www.whistlestopbar.com"),
                   ("Grand Ole BBQ", "https://grandolebbq.com")]:
    try:
        r = get(base + "/wp-json/tribe/events/v1/events?per_page=5")
        if r.status_code == 200 and r.headers.get("content-type","").startswith("application/json"):
            j = r.json()
            evs = j.get("events", [])
            print("  %-18s OK total=%s sample=%s" % (name, j.get("total"), (evs[0]["title"] if evs else "-")))
        else:
            print("  %-18s status=%s ct=%s" % (name, r.status_code, r.headers.get("content-type","")[:20]))
    except Exception as e:
        print("  %-18s ERR %s" % (name, str(e)[:50]))

print("\n=== retry timed-out sites (http+https) ===")
for name, host in [("Ken Club","kenclubsd.com"), ("Soda Bar","sodabarmusic.com"), ("Banshee Bar","bansheebar.com")]:
    for scheme in ("https://www.","https://","http://www."):
        try:
            r = get(scheme+host, timeout=40)
            gen = re.search(r'name=["\']generator["\'] content=["\']([^"\']+)', r.text)
            tw = "ticketweb" in r.text; st="seetickets" in r.text; dice="dice.fm" in r.text
            tribe="tribe-events" in r.text or "tribe_events" in r.text
            print("  %-11s %s -> %s len=%d gen=%s tw=%s seetix=%s dice=%s tribe=%s" % (
                name, scheme+host, r.status_code, len(r.text), (gen.group(1)[:18] if gen else "-"), tw, st, dice, tribe))
            break
        except Exception as e:
            print("  %-11s %s ERR %s" % (name, scheme+host, str(e)[:40]))

print("\n=== TicketWeb cluster: look for data source ===")
for name, base in [("Belly Up","https://bellyup.com"), ("Music Box","https://musicboxsd.com"),
                   ("The Sound","https://thesoundsd.com"), ("Brick By Brick","https://www.brickbybrick.com")]:
    try:
        r = get(base)
        t = r.text
        # ticketweb external links
        tw = re.findall(r'ticketweb\.com/[^\s"\'<>]+', t)
        # any /events or shows nav
        evpages = re.findall(r'href=["\']([^"\']*(?:event|show|calendar|shows)[^"\']*)["\']', t, re.I)
        print("  %-14s twlinks=%d ev-nav=%s" % (name, len(tw), list(dict.fromkeys(evpages))[:4]))
    except Exception as e:
        print("  %-14s ERR %s" % (name, str(e)[:50]))

print("\n=== Squarespace Black Cat / Wix / SOMA / others ===")
for name, url in [("Black Cat json","https://www.blackcatsd.com?format=json"),
                  ("SOMA","https://www.somasandiego.com"),
                  ("Tower Bar","https://www.thetowerbar.com"),
                  ("Winston's","https://winstonsob.com")]:
    try:
        r = get(url)
        t = r.text
        markers = {k: (k in t) for k in ["dice.fm","ticketweb","seetickets","eventbrite","tixr","Collection","tribe-events","fullcalendar","data-aid=\"MENU"]}
        on = [k for k,v in markers.items() if v]
        print("  %-14s status=%s len=%d markers=%s" % (name, r.status_code, len(t), on))
    except Exception as e:
        print("  %-14s ERR %s" % (name, str(e)[:50]))
