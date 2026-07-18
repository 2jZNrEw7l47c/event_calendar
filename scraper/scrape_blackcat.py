"""Black Cat Bar (blackcatbar.wordpress.com) — image-only schedule.

Note: blackcatsd.com (the URL in the original listing) is an unrelated yoga
studio; the bar's real site is the WordPress one. Like Deano's, they post their
calendar as a monthly image on /calendar/ (e.g. bcbjuly2026.jpg), so we grab
the current image and the page shows it in a dialog (see FLYER_SCRAPERS).

Discovery: first content image under wp-content/uploads on the calendar page,
skipping the small site-logo images (a width query < 300 or 'neoncat' name).
"""

import os
import re
import datetime

import requests

import common

PAGE = "https://blackcatbar.wordpress.com/calendar/"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_IMG = re.compile(
    r'src="(https://blackcatbar\.wordpress\.com/wp-content/uploads/[^"]+?\.(?:jpe?g|png))(\?[^"]*)?"',
    re.I)


def scrape(today=None, download=True):
    resp = requests.get(PAGE, headers=common.UA, timeout=30)
    resp.raise_for_status()
    html = common.decode(resp)

    flyer_url = None
    for m in _IMG.finditer(html):
        base, query = m.group(1), m.group(2) or ""
        if "neoncat" in base.lower():
            continue
        wm = re.search(r"[?&]w=(\d+)", query)
        if wm and int(wm.group(1)) < 300:      # tiny logo/thumbnail
            continue
        flyer_url = base + "?w=2000"
        break
    if not flyer_url:
        return None

    result = {
        "source": flyer_url,
        "page": PAGE,
        "fetched": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "image": None,
        "label": "this month's calendar",
    }

    if download:
        img = requests.get(flyer_url, headers=common.UA, timeout=60)
        img.raise_for_status()
        ext = "png" if "png" in img.headers.get("content-type", "") else "jpg"
        rel = "data/blackcat-flyer." + ext
        out = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as f:
            f.write(img.content)
        result["image"] = rel
        result["bytes"] = len(img.content)

    return result


if __name__ == "__main__":
    r = scrape()
    if not r:
        print("Black Cat: flyer not found")
    else:
        for k, v in r.items():
            print("  %-8s %s" % (k, v))
