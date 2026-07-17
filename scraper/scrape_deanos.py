"""Fetch Deano's Pub's current events flyer from https://deanospub.com/

Deano's publishes its schedule as a single graphic (a stylized flyer) under the
homepage's "This week's events!" section, rather than as text. There's no
reliable, non-AI way to turn that artwork into structured event rows, so instead
of scraping the events we grab the flyer image itself and let the page show it
in a dialog. Always accurate, and it can't break when they restyle the flyer.

Discovery is positional: find the "This week's events" heading, then take the
first hosted image after it. That keeps working when they swap in a new flyer
(the filename is a content hash that changes each update).
"""

import os
import re
import datetime

import requests

import common

PAGE = "https://deanospub.com/"
ACCOUNT = "dacbddb2-8c9d-48e4-b193-c142995a101b"   # Deano's GoDaddy media account id
# Full-res render transform for the wsimg CDN.
RENDER = "/:/rs=w:2480,cg:true,m"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_HEADING = re.compile(r"This\s*week.{0,3}s?\s*events", re.I)
_ASSET = re.compile(
    r"(?:https?:)?//img\d\.wsimg\.com/isteam/ip/" + ACCOUNT +
    r"/([^\s\"'\\)]+?\.(?:png|jpe?g))", re.I)


def find_flyer_base(html):
    """Return the CDN base URL of the current flyer, or None."""
    m = _HEADING.search(html)
    search_from = m.end() if m else 0
    m2 = _ASSET.search(html, search_from)
    if not m2:
        return None
    url = m2.group(0)
    if url.startswith("//"):
        url = "https:" + url
    # Strip any existing /:/ transform to get the clean asset base.
    return url.split("/:/")[0]


def scrape(today=None, download=True):
    today = today or datetime.date.today()
    resp = requests.get(PAGE, headers=common.UA, timeout=30)
    resp.raise_for_status()

    base = find_flyer_base(resp.text)
    if not base:
        return None

    source = base + RENDER
    result = {
        "source": source,
        "page": PAGE,
        "fetched": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "image": None,
    }

    if download:
        img = requests.get(source, headers=common.UA, timeout=60)
        img.raise_for_status()
        ext = "png" if "png" in img.headers.get("content-type", "") else "jpg"
        rel = "data/deanos-flyer." + ext
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
        print("Deano's: flyer not found")
    else:
        print("Deano's flyer:")
        for k, v in r.items():
            print("  %-8s %s" % (k, v))
