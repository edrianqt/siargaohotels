"""Pull content out of the existing WordPress site through its public REST API.

    flask --app wsgi import-wp                 # posts, pages, categories (+ listings if exposed)
    flask --app wsgi download-media            # copy wp-content/uploads images locally

Only public data is read; nothing is written back to WordPress.
"""
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from flask import current_app

from .db import execute, insert, query, update
from .helpers import KINDS

UA = {"User-Agent": "SiargaoHotels-Migration/1.0"}

# WordPress pages that are rebuilt natively in Flask — don't overwrite them with Elementor markup.
SKIP_PAGES = {"home", "hotels", "tours", "rentals", "contact", "blog", "cart", "checkout", "my-account",
              "user-dashboard", "page-user-setting", "sample-page", "search-result"}

SHORTCODE = re.compile(r"\[/?[a-zA-Z_][^\]]*\]")


def _get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8")), r.headers


def _paged(base, endpoint, params="", echo=print):
    page = 1
    while True:
        url = f"{base}/wp-json/wp/v2/{endpoint}?per_page=100&page={page}{params}"
        try:
            data, headers = _get(url)
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):  # past the last page, or endpoint not exposed
                if page == 1:
                    echo(f"  - /{endpoint} not available ({e.code})")
                return
            raise
        yield from data
        if page >= int(headers.get("X-WP-TotalPages", 1)):
            return
        page += 1


def clean(content: str) -> str:
    content = SHORTCODE.sub("", content or "")
    return content.strip()


def _featured(item):
    try:
        return item["_embedded"]["wp:featuredmedia"][0]["source_url"]
    except (KeyError, IndexError, TypeError):
        return ""


def _text(field):
    return html.unescape(re.sub("<[^>]+>", "", (field or {}).get("rendered", ""))).strip()


def run_import(site, include_listings=True, echo=print):
    echo(f"Importing from {site}")

    cats = {}
    for c in _paged(site, "categories", echo=echo):
        row = query("SELECT id FROM categories WHERE slug = ?", (c["slug"],), one=True)
        cats[c["id"]] = row["id"] if row else insert("categories", {"slug": c["slug"], "name": html.unescape(c["name"])})
    echo(f"  ✓ {len(cats)} categories")

    n = 0
    for p in _paged(site, "posts", "&_embed=1", echo=echo):
        data = {
            "slug": p["slug"], "title": _text(p["title"]), "excerpt": _text(p.get("excerpt")),
            "body": clean(p["content"]["rendered"]), "image_url": _featured(p),
            "category_id": cats.get((p.get("categories") or [None])[0]),
            "published_at": p["date"].replace("T", " "), "published": 1 if p.get("status") == "publish" else 0,
        }
        row = query("SELECT id FROM posts WHERE slug = ?", (p["slug"],), one=True)
        update("posts", row["id"], data) if row else insert("posts", data)
        n += 1
    echo(f"  ✓ {n} posts")

    n = 0
    for p in _paged(site, "pages", "&_embed=1", echo=echo):
        if p["slug"] in SKIP_PAGES:
            continue
        data = {"slug": p["slug"], "title": _text(p["title"]), "body": clean(p["content"]["rendered"])}
        row = query("SELECT id FROM pages WHERE slug = ?", (p["slug"],), one=True)
        if row and p["slug"] == "car-and-motorcycle-rentals":
            continue  # keep the hand-cleaned copy from the seed
        update("pages", row["id"], data) if row else insert("pages", data)
        n += 1
    echo(f"  ✓ {n} pages")

    if include_listings:
        rest_names = {"hotel": ["st_hotel"], "tour": ["st_tours", "st_tour"], "rental": ["st_rental", "st_rentals"],
                      "car": ["st_cars", "st_car"]}
        for kind, meta in KINDS.items():
            n = 0
            items = []
            for name in rest_names[kind]:
                items = list(_paged(site, name, "&_embed=1", echo=lambda *_: None))
                if items:
                    break
            if not items:
                echo(f"  - {meta['plural']}: not exposed in the WordPress REST API (seeded content kept)")
            for p in items:
                body = clean(p["content"]["rendered"])
                row = query("SELECT id, description, image_url FROM listings WHERE kind = ? AND slug = ?",
                            (kind, p["slug"]), one=True)
                if row:
                    changes = {}
                    if body:  # the original WordPress text replaces the seeded write-up
                        changes["description"] = body
                    if _featured(p) and not row["image_url"]:
                        changes["image_url"] = _featured(p)
                    if changes:
                        update("listings", row["id"], changes)
                else:
                    insert("listings", {"kind": kind, "slug": p["slug"], "title": _text(p["title"]),
                                        "description": body, "image_url": _featured(p),
                                        "price_unit": meta["unit"], "published": 0})
                n += 1
            if n:
                echo(f"  ✓ {n} {meta['plural'].lower()} (new ones are saved as drafts — set price & publish in admin)")
    echo("Done.")


# --------------------------------------------------------------------- media
TEXT_COLUMNS = {
    "listings": ["image_url", "gallery", "description", "policies"],
    "rooms": ["image_url", "description"],
    "locations": ["image_url", "description"],
    "posts": ["image_url", "body"],
    "pages": ["body"],
    "faqs": ["answer"],
}


def localize_media(host="siargaohotels.ph", echo=print):
    pattern = re.compile(rf"https?://(?:www\.)?{re.escape(host)}/wp-content/uploads/([^\s\"'<>)]+?\.(?:jpe?g|png|gif|webp|svg))",
                         re.IGNORECASE)
    out_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "wp"
    cache = {}

    def fetch(match):
        rel = urllib.parse.unquote(match.group(1))
        if rel in cache:
            return cache[rel]
        target = out_dir / rel
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                req = urllib.request.Request(match.group(0), headers=UA)
                with urllib.request.urlopen(req, timeout=60) as r:
                    target.write_bytes(r.read())
                echo(f"  ↓ {rel}")
            except Exception as exc:
                echo(f"  ! {rel}: {exc}")
                cache[rel] = match.group(0)
                return cache[rel]
        cache[rel] = f"/static/uploads/wp/{rel}"
        return cache[rel]

    for table, cols in TEXT_COLUMNS.items():
        for row in query(f"SELECT id, {', '.join(cols)} FROM {table}"):
            changes = {c: pattern.sub(fetch, row[c]) for c in cols if row[c] and pattern.search(row[c])}
            if changes:
                update(table, row["id"], changes)
    for row in query("SELECT key, value FROM settings"):
        if pattern.search(row["value"] or ""):
            execute("UPDATE settings SET value = ? WHERE key = ?", (pattern.sub(fetch, row["value"]), row["key"]))
    echo(f"Localized {len(cache)} images into {out_dir}")
    echo("Note: images referenced only in templates (home page tiles, default logo) — update them in admin Settings "
         "or the templates after downloading.")
