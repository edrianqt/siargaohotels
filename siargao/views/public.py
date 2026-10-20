"""Public website: home, archives, detail pages, locations, blog, pages, contact."""
import math
import re
from datetime import datetime
from urllib.parse import urlencode
from xml.sax.saxutils import escape

from flask import (Blueprint, Response, abort, current_app, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)

from ..db import execute, get_settings, insert, query
from ..helpers import (ARCHIVE_TO_KIND, CATEGORIES, KINDS, PREFIX_TO_KIND,
                       RATING_BANDS, REVIEW_ASPECTS, enrich, money, parse_facilities, price_line, today_iso)
from ..mailer import send_mail

bp = Blueprint("public", __name__)

BASE_SQL = ("SELECT l.*, loc.name AS location_name, loc.slug AS location_slug "
            "FROM listings l LEFT JOIN locations loc ON loc.id = l.location_id ")


def listings(kind, limit=None, location_id=None, exclude=None, featured_first=True):
    sql = BASE_SQL + "WHERE l.kind = ? AND l.published = 1"
    params = [kind]
    if location_id:
        sql += " AND l.location_id = ?"
        params.append(location_id)
    if exclude:
        sql += " AND l.id != ?"
        params.append(exclude)
    sql += " ORDER BY " + ("l.featured DESC, " if featured_first else "") + "l.id DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    return enrich(query(sql, params))


# ---------------------------------------------------------------- home
@bp.route("/")
def home():
    return render_template(
        "home.html",
        hotels=listings("hotel", 8),
        tours=listings("tour", 8),
        rentals=listings("rental", 4),
        posts=recent_posts(4),
        faqs=query("SELECT * FROM faqs ORDER BY position, id"),
        locations=query("SELECT * FROM locations ORDER BY position, name"),
        map_points=map_points(),
    )


def map_points():
    """Towns for the interactive island map, with how many listings of each type they have."""
    points = []
    for loc in query("SELECT * FROM locations ORDER BY position"):
        counts = {r["kind"]: r["n"] for r in query(
            "SELECT kind, COUNT(*) n FROM listings WHERE location_id = ? AND published = 1 GROUP BY kind", (loc["id"],))}
        points.append({"slug": loc["slug"], "name": loc["name"], "image": loc["image_url"],
                       "blurb": re.sub("<[^>]+>", "", loc["description"] or "").split(". ")[0].strip().rstrip(".") + ".",
                       "url": url_for("public.location", slug=loc["slug"]),
                       "hotels": counts.get("hotel", 0) + counts.get("rental", 0),
                       "tours": counts.get("tour", 0), "cars": counts.get("car", 0)})
    return points


def recent_posts(n):
    return query(
        "SELECT p.*, c.name AS category_name, c.slug AS category_slug FROM posts p "
        "LEFT JOIN categories c ON c.id = p.category_id WHERE p.published = 1 "
        "ORDER BY p.published_at DESC LIMIT ?", (n,))


# ---------------------------------------------------------------- archives
SORTS = {
    "new": ("New", lambda x: -x["id"]),
    "price_asc": ("Price: Low to High", lambda x: x["price"]),
    "price_desc": ("Price: High to Low", lambda x: -x["price"]),
    "name_asc": ("Name: a - z", lambda x: x["title"].lower()),
    "name_desc": ("Name: z - a", None),
}


@bp.route("/hotels/", defaults={"archive": "hotels"})
@bp.route("/tours/", defaults={"archive": "tours"})
@bp.route("/rentals/", defaults={"archive": "rentals"})
@bp.route("/car-and-motorcycle-rentals/", defaults={"archive": "car-and-motorcycle-rentals"})
@bp.route("/<any(hotels,tours,rentals,'car-and-motorcycle-rentals'):archive>/page/<int:page>/")
def archive(archive, page=None):
    kind = ARCHIVE_TO_KIND[archive]
    a = request.args
    sql = BASE_SQL + "WHERE l.kind = ? AND l.published = 1"
    params = [kind]

    loc = a.get("location", "")
    if loc:
        sql += " AND (loc.slug = ? OR CAST(loc.id AS TEXT) = ? OR loc.zipcode = ?)"
        params += [loc, loc, loc]
    if a.get("q"):
        sql += " AND (l.title LIKE ? OR l.address LIKE ?)"
        params += [f"%{a['q']}%"] * 2
    cats = [c for c in a.getlist("category") if c]
    if cats:
        sql += f" AND l.category IN ({','.join('?' * len(cats))})"
        params += cats
    for key, op in (("price_min", ">="), ("price_max", "<=")):
        try:
            if a.get(key):
                sql += f" AND l.price {op} ?"
                params.append(float(a[key]))
        except ValueError:
            pass
    guests = a.get("adults", 0, type=int) + a.get("children", 0, type=int)
    if kind == "rental" and guests:
        sql += " AND (l.seats = 0 OR l.seats >= ?)"
        params.append(guests)

    items = enrich(query(sql, params))

    wanted = set(a.getlist("rating"))
    if wanted:
        def band(score):
            for floor, _label, key in RATING_BANDS:
                if score >= floor:
                    return key
            return None
        items = [i for i in items if band(i["rating"]) in wanted]

    sort = a.get("sort", "new")
    if sort == "name_desc":
        items.sort(key=lambda x: x["title"].lower(), reverse=True)
    else:
        items.sort(key=SORTS.get(sort, SORTS["new"])[1])
    if sort == "new":
        items.sort(key=lambda x: -x["featured"])

    per = current_app.config["PER_PAGE"]
    page = page or a.get("page", 1, type=int)
    pages = max(math.ceil(len(items) / per), 1)
    page = min(max(page, 1), pages)
    total = len(items)
    shown = items[(page - 1) * per: page * per]

    def page_url(p):
        qs = urlencode([(k, v) for k, v in a.items(multi=True) if k != "page"])
        base = url_for("public.archive", archive=archive) if p == 1 else \
            url_for("public.archive", archive=archive, page=p)
        return base + (f"?{qs}" if qs else "")

    all_prices = [r["price"] for r in query("SELECT price FROM listings WHERE kind=? AND published=1", (kind,))]
    page_obj = query("SELECT * FROM pages WHERE slug = ?", (archive,), one=True)
    return render_template(
        "archive.html", kind=kind, meta=KINDS[kind], items=shown, total=total,
        page=page, pages=pages, per=per, sort=sort, sorts=SORTS, args=a,
        rating_bands=RATING_BANDS, categories=CATEGORIES.get(kind, []),
        price_bounds=(min(all_prices, default=0), max(all_prices, default=0)),
        locations=query("SELECT * FROM locations ORDER BY position, name"),
        intro=page_obj, page_url=page_url,
    )


# ---------------------------------------------------------------- details
@bp.route("/<any(st_hotel,st_tour,st_rental,st_car):prefix>/<slug>/")
def detail(prefix, slug):
    kind = PREFIX_TO_KIND[prefix]
    row = query(BASE_SQL + "WHERE l.kind = ? AND l.slug = ?", (kind, slug), one=True)
    is_admin = bool(g.user and g.user["is_admin"])
    if not row or (not row["published"] and not is_admin):
        abort(404)
    item = enrich([row])[0]
    reviews = query("SELECT * FROM reviews WHERE listing_id = ? AND approved = 1 ORDER BY created_at DESC", (item["id"],))
    aspects = {}
    if reviews:
        for key, label in REVIEW_ASPECTS:
            aspects[label] = round(sum(r[key] for r in reviews) / len(reviews), 1)
    bands = {label: 0 for _f, label, _k in RATING_BANDS}
    for r in reviews:
        score = sum(r[k] for k, _ in REVIEW_ASPECTS) / 6
        for floor, label, _k in RATING_BANDS:
            if score >= floor:
                bands[label] += 1
                break
    return render_template(
        "detail.html", item=item, kind=kind, meta=KINDS[kind],
        rooms=query("SELECT * FROM rooms WHERE listing_id = ? ORDER BY price", (item["id"],)),
        reviews=reviews, aspects=aspects, bands=bands, review_aspects=REVIEW_ASPECTS,
        facilities=parse_facilities(item["facilities"]),
        nearby=listings(kind, 4, location_id=item["location_id"], exclude=item["id"]),
        start=request.args.get("start", today_iso(0)),
        end=request.args.get("end", today_iso(max(item["min_stay"] or 1, 1))),
        adults=request.args.get("adults", 1, type=int),
        children=request.args.get("children", 0, type=int),
    )


@bp.route("/hotel_room/<slug>/")
def room_redirect(slug):
    room = query("SELECT r.*, l.slug AS hslug FROM rooms r JOIN listings l ON l.id = r.listing_id "
                 "WHERE r.slug = ?", (slug,), one=True)
    if not room:
        abort(404)
    return redirect(url_for("public.detail", prefix="st_hotel", slug=room["hslug"]) + "#rooms", 301)


@bp.post("/<any(st_hotel,st_tour,st_rental,st_car):prefix>/<slug>/review")
def add_review(prefix, slug):
    item = query("SELECT * FROM listings WHERE kind = ? AND slug = ?", (PREFIX_TO_KIND[prefix], slug), one=True)
    if not item:
        abort(404)
    f = request.form
    if f.get("website"):  # honeypot
        return redirect(url_for("public.detail", prefix=prefix, slug=slug))
    name, body = f.get("name", "").strip(), f.get("body", "").strip()
    if not name or not body:
        flash("Please add your name and a short review.", "danger")
        return redirect(url_for("public.detail", prefix=prefix, slug=slug) + "#write-review")
    data = {"listing_id": item["id"], "name": name[:120], "email": f.get("email", "")[:200],
            "title": f.get("title", "")[:200], "body": body[:5000], "approved": 0}
    for key, _label in REVIEW_ASPECTS:
        data[key] = min(max(f.get(key, 5, type=float), 1), 5)
    insert("reviews", data)
    flash("Thank you! Your review will appear once approved.", "success")
    return redirect(url_for("public.detail", prefix=prefix, slug=slug) + "#reviews")


@bp.post("/<any(st_hotel,st_tour,st_rental,st_car):prefix>/<slug>/inquiry")
def inquiry(prefix, slug):
    item = query("SELECT * FROM listings WHERE kind = ? AND slug = ?", (PREFIX_TO_KIND[prefix], slug), one=True)
    if not item:
        abort(404)
    f = request.form
    if not f.get("name") or not f.get("email") or not f.get("message"):
        flash("Name, email and message are required.", "danger")
    elif not f.get("website"):
        insert("messages", {"name": f["name"], "email": f["email"], "phone": f.get("phone", ""),
                            "subject": f"Inquiry: {item['title']}", "message": f["message"],
                            "listing_id": item["id"]})
        send_mail(current_app.config["ADMIN_NOTIFY"], f"Inquiry: {item['title']}",
                  f"From {f['name']} <{f['email']}> {f.get('phone','')}\n\n{f['message']}")
        flash("Your inquiry was sent. We'll get back to you shortly.", "success")
    return redirect(url_for("public.detail", prefix=prefix, slug=slug))


@bp.route("/api/quote")
def quote():
    """Live price estimate for the booking box (same rules as the cart)."""
    a = request.args
    item = query("SELECT * FROM listings WHERE id = ? AND published = 1", (a.get("listing_id", type=int),), one=True)
    if not item:
        return jsonify(error="Listing not found"), 404
    room = None
    if a.get("room_id", type=int):
        room = query("SELECT * FROM rooms WHERE id = ? AND listing_id = ?", (a.get("room_id", type=int), item["id"]), one=True)
    qty, unit, total, desc = price_line(dict(item), room, a.get("start"), a.get("end"),
                                        max(a.get("adults", 1, type=int), 1), max(a.get("children", 0, type=int), 0),
                                        max(a.get("rooms", 1, type=int), 1))
    return jsonify(total=total, total_fmt=money(total), unit_fmt=money(unit), qty=qty, desc=desc)


@bp.route("/wishlist/")
def wishlist():
    """Saved listings. IDs live in the visitor's browser (localStorage) and arrive as ?ids=1,2,3."""
    ids = [int(i) for i in request.args.get("ids", "").split(",") if i.isdigit()][:60]
    items = []
    if ids:
        rows = enrich(query(BASE_SQL + f"WHERE l.published = 1 AND l.id IN ({','.join('?' * len(ids))})", ids))
        order = {i: n for n, i in enumerate(ids)}
        items = sorted(rows, key=lambda r: order.get(r["id"], 0))
    return render_template("wishlist.html", items=items, loaded="ids" in request.args)


# ---------------------------------------------------------------- locations
@bp.route("/st_location/<slug>/")
def location(slug):
    loc = query("SELECT * FROM locations WHERE slug = ?", (slug,), one=True)
    if not loc:
        abort(404)
    sections = [(k, KINDS[k], listings(k, 8, location_id=loc["id"])) for k in KINDS]
    return render_template("location.html", loc=loc, sections=sections)


# ---------------------------------------------------------------- blog
@bp.route("/blog/")
@bp.route("/blog")
@bp.route("/blog/page/<int:page>/")
def blog(page=1):
    return _post_list(page=page)


@bp.route("/category/<slug>/")
@bp.route("/category/<slug>/page/<int:page>/")
def category(slug, page=1):
    cat = query("SELECT * FROM categories WHERE slug = ?", (slug,), one=True)
    if not cat:
        abort(404)
    return _post_list(page=page, category=cat)


def _post_list(page=1, category=None):
    per = 9
    where, params = "WHERE p.published = 1", []
    if category:
        where += " AND p.category_id = ?"
        params.append(category["id"])
    total = query(f"SELECT COUNT(*) n FROM posts p {where}", params, one=True)["n"]
    rows = query(
        "SELECT p.*, c.name AS category_name, c.slug AS category_slug FROM posts p "
        f"LEFT JOIN categories c ON c.id = p.category_id {where} "
        "ORDER BY p.published_at DESC LIMIT ? OFFSET ?", (*params, per, (page - 1) * per))
    return render_template("blog.html", posts=rows, page=page, pages=max(math.ceil(total / per), 1),
                           category=category, categories=query("SELECT * FROM categories ORDER BY name"))


# ---------------------------------------------------------------- contact & forms
@bp.route("/contact/", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        f = request.form
        if f.get("website"):
            return redirect(url_for("public.contact"))
        if not f.get("name") or not f.get("email") or not f.get("message"):
            flash("Name, email and message are required.", "danger")
        else:
            insert("messages", {k: f.get(k, "")[:5000] for k in ("name", "email", "phone", "address", "message")})
            send_mail(current_app.config["ADMIN_NOTIFY"], "New contact message",
                      f"From {f['name']} <{f['email']}> {f.get('phone','')}\n{f.get('address','')}\n\n{f['message']}")
            flash("Thanks! A member of our team will personally reach out shortly.", "success")
            return redirect(url_for("public.contact"))
    return render_template("contact.html")


@bp.post("/subscribe")
def subscribe():
    email = request.form.get("email", "").strip().lower()
    if request.form.get("website"):
        return redirect(request.referrer or url_for("public.home"))
    if "@" not in email:
        flash("Please enter a valid email address.", "danger")
    else:
        execute("INSERT OR IGNORE INTO subscribers(email) VALUES (?)", (email,))
        flash("You're subscribed! Watch your inbox for Siargao deals & tips.", "success")
    return redirect((request.referrer or url_for("public.home")).split("#")[0] + "#newsletter")


@bp.route("/currency/<code>")
def set_currency(code):
    if code.upper() in ("PHP", "USD"):
        session["currency"] = code.upper()
    return redirect(request.referrer or url_for("public.home"))


@bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results, posts = [], []
    if q:
        like = f"%{q}%"
        results = enrich(query(BASE_SQL + "WHERE l.published = 1 AND (l.title LIKE ? OR l.address LIKE ? "
                               "OR l.description LIKE ?) ORDER BY l.kind, l.title", (like, like, like)))
        posts = query("SELECT * FROM posts WHERE published = 1 AND (title LIKE ? OR body LIKE ?) "
                      "ORDER BY published_at DESC LIMIT 12", (like, like))
    return render_template("search.html", q=q, results=results, posts=posts)


# ---------------------------------------------------------------- SEO
@bp.route("/robots.txt")
def robots():
    return Response(f"User-agent: *\nDisallow: /admin/\nDisallow: /cart/\n"
                    f"Sitemap: {request.url_root}sitemap.xml\n", mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap():
    root = request.url_root.rstrip("/")
    urls = [url_for("public.home"), url_for("public.blog"), url_for("public.contact")]
    urls += [url_for("public.archive", archive=m["archive"]) for m in KINDS.values()]
    for r in query("SELECT kind, slug FROM listings WHERE published = 1"):
        urls.append(url_for("public.detail", prefix=KINDS[r["kind"]]["prefix"], slug=r["slug"]))
    urls += [url_for("public.location", slug=r["slug"]) for r in query("SELECT slug FROM locations")]
    urls += [url_for("public.page_or_post", slug=r["slug"]) for r in query("SELECT slug FROM posts WHERE published=1")]
    urls += [url_for("public.page_or_post", slug=r["slug"]) for r in query("SELECT slug FROM pages")]
    xml = "".join(f"<url><loc>{escape(root + u)}</loc></url>" for u in dict.fromkeys(urls))
    return Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/'
                    f'sitemap/0.9">{xml}</urlset>', mimetype="application/xml")


# ---------------------------------------------------------------- WordPress-style /<slug>/
@bp.route("/<slug>/")
@bp.route("/<slug>")
def page_or_post(slug):
    post = query("SELECT p.*, c.name AS category_name, c.slug AS category_slug FROM posts p "
                 "LEFT JOIN categories c ON c.id = p.category_id WHERE p.slug = ? AND p.published = 1",
                 (slug,), one=True)
    if post:
        related = query("SELECT * FROM posts WHERE published = 1 AND id != ? ORDER BY "
                        "(category_id = ?) DESC, published_at DESC LIMIT 3", (post["id"], post["category_id"]))
        return render_template("post.html", post=post, related=related)
    page = query("SELECT * FROM pages WHERE slug = ?", (slug,), one=True)
    if page:
        return render_template("page.html", page=page)
    abort(404)


@bp.app_template_filter("datefmt")
def datefmt(value, fmt="%B %d, %Y"):
    for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(value)[:19], pattern).strftime(fmt)
        except ValueError:
            continue
    return value


@bp.app_context_processor
def seo_defaults():
    return {"default_description": get_settings().get("meta_description", "")}
