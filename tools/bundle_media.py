"""Download every siargaohotels.ph photo referenced by this project into siargao/static/uploads/wp/.

    python tools/bundle_media.py

Scans the content, seed, settings and templates for wp-content/uploads URLs and saves each file
under the same year/month path. Already-downloaded files are skipped, so it is safe to re-run.
The site automatically serves the local copy of any photo found here.
"""
import concurrent.futures as cf
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "siargao" / "static" / "uploads" / "wp"
PATTERN = re.compile(
    r"https?://(?:www\.)?siargaohotels\.ph/wp-content/uploads/([\w\-./%]+?\.(?:jpe?g|png|gif|webp|svg))", re.I)
# Paths built from fragments in content.py, e.g. UP + "2026/02/x.jpg" or f"2026/02/{n}-870x555.jpg"
FRAGMENT = re.compile(r"(?:[\"']|\{UP\})(20\d\d/\d\d/[^\"'{}\s]+?\.(?:jpe?g|png|gif|webp|svg))", re.I)


def collect():
    paths = set()
    for f in list((ROOT / "siargao").rglob("*.py")) + list((ROOT / "siargao" / "templates").rglob("*.html")):
        text = f.read_text(encoding="utf-8")
        paths.update(m.group(1) for m in PATTERN.finditer(text))
        if f.name in ("content.py", "seed.py"):
            paths.update(m.group(1) for m in FRAGMENT.finditer(text))
    # galleries/images that content.py builds with f-strings
    sys.path.insert(0, str(ROOT))
    from siargao import content as C
    blob = repr([C.LOCATIONS, C.HOTELS, C.TOURS, C.CARS, C.POSTS])
    paths.update(m.group(1) for m in PATTERN.finditer(blob))
    for c in C.CARS:
        paths.update([c["image"], *c["gallery"]])
    for p in C.POSTS:
        paths.add(p[3])
    for loc in C.LOCATIONS:
        paths.update(loc["gallery"])
    return sorted(urllib.parse.unquote(p) for p in paths)


def fetch(rel):
    target = OUT / rel
    if target.exists() and target.stat().st_size:
        return rel, "cached", target.stat().st_size
    url = "https://siargaohotels.ph/wp-content/uploads/" + urllib.parse.quote(rel)
    req = urllib.request.Request(url, headers={"User-Agent": "SiargaoHotels-Migration/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return rel, "downloaded", len(data)


def main():
    rels = collect()
    print(f"{len(rels)} photos referenced")
    ok, failed, total = 0, [], 0
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, r): r for r in rels}
        for fut in cf.as_completed(futures):
            rel = futures[fut]
            try:
                _, status, size = fut.result()
                ok += 1
                total += size
            except Exception as exc:
                failed.append((rel, str(exc)))
    print(f"{ok} saved in {OUT} ({total / 1e6:.1f} MB)")
    for rel, err in sorted(failed):
        print(f"  ! {rel}: {err}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
