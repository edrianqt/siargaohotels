"""Fetch the full-size original of every resized WordPress photo and save a sharp, web-optimised copy.

    python tools/upgrade_media.py

WordPress stores small copies like `photo-931x594.jpg` next to the original `photo.jpg`.
For each small copy in siargao/static/uploads/wp/ this downloads the original and saves it
(longest side capped at 2000 px, quality 82) at the original's path. Originals already present
but larger than 2000 px are shrunk the same way. Safe to re-run.
"""
import concurrent.futures as cf
import io
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
WP = ROOT / "siargao" / "static" / "uploads" / "wp"
BASE = "https://siargaohotels.ph/wp-content/uploads/"
SIZED = re.compile(r"^(?P<stem>.+)-\d+x\d+(?P<ext>\.(?:jpe?g|png|webp))$", re.I)
MAX = 2000


def optimise(data: bytes, target: Path):
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img)
    if max(img.size) > MAX:
        img.thumbnail((MAX, MAX), Image.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix.lower() in (".jpg", ".jpeg"):
        img.convert("RGB").save(target, "JPEG", quality=82, optimize=True, progressive=True)
    else:
        img.save(target, optimize=True)
    return img.size


def upgrade(original_rel: str):
    target = WP / original_rel
    if target.exists():
        with Image.open(target) as im:
            if max(im.size) <= MAX:
                return original_rel, "ok", im.size
        return original_rel, "shrunk", optimise(target.read_bytes(), target)
    url = BASE + urllib.parse.quote(original_rel)
    req = urllib.request.Request(url, headers={"User-Agent": "SiargaoHotels-Migration/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    return original_rel, "downloaded", optimise(data, target)


def main():
    originals = set()
    for f in WP.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(WP).as_posix()
        m = SIZED.match(rel)
        originals.add(m.group("stem") + m.group("ext") if m else rel)
    originals = sorted(o for o in originals if not o.lower().endswith(".svg"))
    ok, failed = 0, []
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(upgrade, o): o for o in originals}
        for fut in cf.as_completed(futures):
            try:
                fut.result()
                ok += 1
            except Exception as exc:
                failed.append((futures[fut], str(exc)))
    print(f"{ok} full-size photos ready, {len(failed)} without an original")
    for rel, err in sorted(failed):
        print(f"  - {rel}: {err}")


if __name__ == "__main__":
    sys.exit(main())
