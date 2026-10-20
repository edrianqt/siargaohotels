"""Admin dashboard — a compact replacement for wp-admin.

Every content type is described once in RESOURCES; list/create/edit/delete screens
are generated from that description.
"""
import csv
import io
import math
import os
import secrets
from pathlib import Path

from flask import (Blueprint, Response, abort, current_app, flash, redirect, render_template,
                   request, url_for)
from werkzeug.utils import secure_filename

from ..db import DEFAULT_SETTINGS, execute, get_settings, insert, query, set_setting, update
from ..helpers import KINDS, admin_required, slugify

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _locations():
    return [("", "— none —")] + [(str(r["id"]), r["name"]) for r in query("SELECT id, name FROM locations ORDER BY name")]


def _categories():
    return [("", "— none —")] + [(str(r["id"]), r["name"]) for r in query("SELECT id, name FROM categories ORDER BY name")]


def _hotels():
    return [(str(r["id"]), r["title"]) for r in query("SELECT id, title FROM listings WHERE kind='hotel' ORDER BY title")]


def _all_listings():
    return [(str(r["id"]), f"{KINDS[r['kind']]['label']}: {r['title']}")
            for r in query("SELECT id, kind, title FROM listings ORDER BY kind, title")]


F = lambda name, label, type="text", **kw: {"name": name, "label": label, "type": type, **kw}  # noqa: E731

RESOURCES = {
    "listings": {
        "label": "Listings", "singular": "Listing", "table": "listings", "order": "kind, featured DESC, id DESC",
        "columns": [("title", "Title"), ("kind", "Type"), ("price", "Price"), ("published", "Live")],
        "search": ["title", "address"], "filter": ("kind", [(k, v["plural"]) for k, v in KINDS.items()]),
        "slug_from": "title",
        "fields": [
            F("kind", "Type", "select", choices=[(k, v["label"]) for k, v in KINDS.items()], required=True),
            F("title", "Title", required=True), F("slug", "Slug (URL)", help="Leave blank to generate from the title."),
            F("location_id", "Location", "select", choices=_locations), F("address", "Address"),
            F("summary", "Short summary", "textarea"), F("description", "Description", "html"),
            F("image_url", "Featured image", "image"), F("gallery", "Gallery (one image URL per line)", "textarea"),
            F("price", "Price from (PHP)", "number"),
            F("price_unit", "Price unit", "select", choices=[("night", "per night"), ("person", "per person"),
                                                             ("day", "per day"), ("booking", "per booking")]),
            F("category", "Category", "select", choices=[("", "—"), ("joiner", "Joiner Tour"), ("private", "Private Tour"),
                                                         ("car", "Car"), ("motorcycle", "Motorcycle")]),
            F("duration", "Duration (tours)"), F("seats", "Seats / max guests", "number"),
            F("transmission", "Transmission (cars)", "select", choices=[("", "—"), ("Auto", "Auto"), ("Manual", "Manual")]),
            F("bedrooms", "Bedrooms (rentals)", "number"), F("phone", "Contact phone"),
            F("facilities", "Facilities", "textarea", help="One group per line, e.g.  Dining & Food Facilities: Breakfast Service, Bar"),
            F("highlights", "Highlights (one per line)", "textarea"),
            F("itinerary", "Itinerary (one per line, e.g. Day 1: Arrival)", "textarea"),
            F("inclusions", "Inclusions (one per line)", "textarea"),
            F("exclusions", "Exclusions (one per line)", "textarea"),
            F("reminders", "Reminders / rental requirements (one per line)", "textarea"),
            F("rate_tiers", "Rate tiers", "textarea",
              help="Tours: group size: price per person (e.g. 4: 3998). Vehicles: days: price per day (e.g. 3: 495)."),
            F("features", "Feature badges (comma separated)"),
            F("start_time", "Pick-up / start time (tours) or delivery hours (cars)"),
            F("check_in", "Check-in time"), F("check_out", "Check-out time"), F("policies", "Policies", "html"),
            F("min_stay", "Minimum nights", "number"), F("owner_name", "Owner / host name"),
            F("map_query", "Map search text", help="Used for the Google map embed. Defaults to the address."),
            F("imported_rating", "Imported rating (0-5)", "number", help="Shown until real reviews are approved."),
            F("imported_reviews", "Imported review count", "number"),
            F("featured", "Featured", "bool"), F("published", "Published", "bool", default=1),
            F("seo_title", "SEO title"), F("seo_description", "SEO description", "textarea"),
        ],
    },
    "rooms": {
        "label": "Hotel rooms", "singular": "Room", "table": "rooms", "order": "listing_id, price",
        "columns": [("name", "Room"), ("listing_id", "Hotel"), ("price", "Price")], "search": ["name"],
        "slug_from": "name",
        "fields": [F("listing_id", "Hotel", "select", choices=_hotels, required=True), F("name", "Room name", required=True),
                   F("slug", "Slug"), F("size_m2", "Size (m²)", "number"), F("beds", "Beds", "number"),
                   F("max_adults", "Max adults", "number"), F("price", "Price per night (PHP)", "number"),
                   F("image_url", "Image", "image"), F("description", "Description", "html")],
    },
    "reviews": {
        "label": "Reviews", "singular": "Review", "table": "reviews", "order": "approved, created_at DESC",
        "columns": [("name", "Guest"), ("title", "Title"), ("listing_id", "Listing"), ("approved", "Approved")],
        "search": ["name", "title", "body"],
        "fields": [F("listing_id", "Listing", "select", choices=_all_listings, required=True), F("name", "Name", required=True),
                   F("email", "Email"), F("title", "Title"), F("body", "Review", "textarea"),
                   *[F(k, l + " (1-5)", "number") for k, l in [("cleanliness", "Cleanliness"), ("comfort", "Comfort"),
                     ("location", "Location"), ("facilities", "Facilities"), ("staff", "Staff"), ("value", "Value")]],
                   F("approved", "Approved", "bool"), F("created_at", "Date")],
    },
    "locations": {
        "label": "Locations", "singular": "Location", "table": "locations", "order": "position, name",
        "columns": [("name", "Name"), ("zipcode", "ZIP"), ("position", "Order")], "search": ["name"], "slug_from": "name",
        "fields": [F("name", "Name", required=True), F("slug", "Slug"), F("zipcode", "ZIP code"),
                   F("description", "Description", "html"), F("image_url", "Image", "image"), F("position", "Menu order", "number")],
    },
    "posts": {
        "label": "Blog posts", "singular": "Post", "table": "posts", "order": "published_at DESC",
        "columns": [("title", "Title"), ("category_id", "Category"), ("published_at", "Date"), ("published", "Live")],
        "search": ["title", "body"], "slug_from": "title",
        "fields": [F("title", "Title", required=True), F("slug", "Slug"), F("category_id", "Category", "select", choices=_categories),
                   F("excerpt", "Excerpt", "textarea"), F("body", "Content", "html"), F("image_url", "Featured image", "image"),
                   F("published_at", "Publish date"), F("published", "Published", "bool", default=1),
                   F("seo_description", "SEO description", "textarea")],
    },
    "categories": {
        "label": "Blog categories", "singular": "Category", "table": "categories", "order": "name",
        "columns": [("name", "Name"), ("slug", "Slug")], "search": ["name"], "slug_from": "name",
        "fields": [F("name", "Name", required=True), F("slug", "Slug")],
    },
    "pages": {
        "label": "Pages", "singular": "Page", "table": "pages", "order": "title",
        "columns": [("title", "Title"), ("slug", "Slug")], "search": ["title", "body"], "slug_from": "title",
        "fields": [F("title", "Title", required=True), F("slug", "Slug",
                     help="Use hotels / tours / rentals / car-and-motorcycle-rentals to add intro text to those archive pages."),
                   F("body", "Content", "html"), F("seo_description", "SEO description", "textarea")],
    },
    "faqs": {
        "label": "FAQs", "singular": "FAQ", "table": "faqs", "order": "position, id",
        "columns": [("question", "Question"), ("position", "Order")], "search": ["question", "answer"],
        "fields": [F("question", "Question", required=True), F("answer", "Answer", "html", required=True),
                   F("position", "Order", "number")],
    },
    "bookings": {
        "label": "Bookings", "singular": "Booking", "table": "bookings", "order": "created_at DESC", "no_create": True,
        "columns": [("ref", "Ref"), ("name", "Guest"), ("total", "Total"), ("status", "Status"), ("created_at", "Date")],
        "search": ["ref", "name", "email"],
        "filter": ("status", [(s, s.title()) for s in ("pending", "confirmed", "completed", "cancelled")]),
        "fields": [F("status", "Status", "select", choices=[(s, s.title()) for s in ("pending", "confirmed", "completed", "cancelled")]),
                   F("name", "Name"), F("email", "Email"), F("phone", "Phone"), F("notes", "Notes", "textarea")],
    },
    "messages": {
        "label": "Messages", "singular": "Message", "table": "messages", "order": "created_at DESC", "no_create": True,
        "columns": [("name", "From"), ("email", "Email"), ("subject", "Subject"), ("created_at", "Date")],
        "search": ["name", "email", "message"],
        "fields": [F("name", "Name"), F("email", "Email"), F("phone", "Phone"), F("address", "Address"),
                   F("subject", "Subject"), F("message", "Message", "textarea")],
    },
    "subscribers": {
        "label": "Subscribers", "singular": "Subscriber", "table": "subscribers", "order": "created_at DESC",
        "columns": [("email", "Email"), ("created_at", "Subscribed")], "search": ["email"],
        "fields": [F("email", "Email", required=True)],
    },
    "users": {
        "label": "Users", "singular": "User", "table": "users", "order": "created_at DESC", "no_create": True,
        "columns": [("name", "Name"), ("email", "Email"), ("is_admin", "Admin")], "search": ["name", "email"],
        "fields": [F("name", "Name"), F("email", "Email"), F("is_admin", "Administrator", "bool")],
    },
}


def _resource(name):
    res = RESOURCES.get(name)
    if not res:
        abort(404)
    return res


def _choices(field):
    c = field.get("choices", [])
    return c() if callable(c) else c


def _lookup_maps():
    return {
        "listing_id": {r["id"]: r["title"] for r in query("SELECT id, title FROM listings")},
        "category_id": {r["id"]: r["name"] for r in query("SELECT id, name FROM categories")},
        "kind": {k: v["label"] for k, v in KINDS.items()},
    }


@bp.app_template_global()
def admin_resources():
    return RESOURCES


# ------------------------------------------------------------------ dashboard
@bp.route("/")
@admin_required
def dashboard():
    count = lambda sql: query(sql, one=True)[0]  # noqa: E731
    stats = {
        "Hotels": count("SELECT COUNT(*) FROM listings WHERE kind='hotel'"),
        "Tours": count("SELECT COUNT(*) FROM listings WHERE kind='tour'"),
        "Rentals": count("SELECT COUNT(*) FROM listings WHERE kind='rental'"),
        "Cars": count("SELECT COUNT(*) FROM listings WHERE kind='car'"),
        "Pending bookings": count("SELECT COUNT(*) FROM bookings WHERE status='pending'"),
        "Reviews to approve": count("SELECT COUNT(*) FROM reviews WHERE approved=0"),
        "Subscribers": count("SELECT COUNT(*) FROM subscribers"),
        "Posts": count("SELECT COUNT(*) FROM posts"),
    }
    return render_template(
        "admin/dashboard.html", stats=stats,
        bookings=query("SELECT * FROM bookings ORDER BY created_at DESC LIMIT 8"),
        messages=query("SELECT * FROM messages ORDER BY created_at DESC LIMIT 6"),
        reviews=query("SELECT r.*, l.title AS listing FROM reviews r JOIN listings l ON l.id = r.listing_id "
                      "WHERE approved = 0 ORDER BY created_at DESC LIMIT 6"),
    )


# ------------------------------------------------------------------ generic CRUD
@bp.route("/<name>/")
@admin_required
def list_view(name):
    res = _resource(name)
    where, params = [], []
    q = request.args.get("q", "").strip()
    if q:
        where.append("(" + " OR ".join(f"{c} LIKE ?" for c in res["search"]) + ")")
        params += [f"%{q}%"] * len(res["search"])
    flt = res.get("filter")
    if flt and request.args.get(flt[0]):
        where.append(f"{flt[0]} = ?")
        params.append(request.args[flt[0]])
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    total = query(f"SELECT COUNT(*) FROM {res['table']} {clause}", params, one=True)[0]
    per, page = 30, request.args.get("page", 1, type=int)
    rows = query(f"SELECT * FROM {res['table']} {clause} ORDER BY {res['order']} LIMIT ? OFFSET ?",
                 (*params, per, (page - 1) * per))
    return render_template("admin/list.html", name=name, res=res, rows=rows, q=q, total=total,
                           page=page, pages=max(math.ceil(total / per), 1), maps=_lookup_maps())


@bp.route("/<name>/new/", methods=["GET", "POST"])
@bp.route("/<name>/<int:row_id>/edit/", methods=["GET", "POST"])
@admin_required
def edit_view(name, row_id=None):
    res = _resource(name)
    if row_id is None and res.get("no_create"):
        abort(404)
    row = query(f"SELECT * FROM {res['table']} WHERE id = ?", (row_id,), one=True) if row_id else None
    if row_id and not row:
        abort(404)
    values = dict(row) if row else {f["name"]: f.get("default", "") for f in res["fields"]}
    if row is None and request.args.get("kind"):
        values["kind"] = request.args["kind"]

    if request.method == "POST":
        data, errors = {}, []
        for f in res["fields"]:
            key, kind = f["name"], f["type"]
            if kind == "bool":
                data[key] = 1 if request.form.get(key) else 0
                continue
            val = request.form.get(key, "")
            if kind == "image":
                upload = request.files.get(key + "_file")
                if upload and upload.filename:
                    val = save_upload(upload) or val
            if kind == "number":
                try:
                    val = float(val) if val not in ("", None) else 0
                    val = int(val) if float(val).is_integer() else val
                except ValueError:
                    errors.append(f"{f['label']} must be a number.")
            if kind == "select" and key.endswith("_id"):
                val = int(val) if str(val).isdigit() else None
            if f.get("required") and val in ("", None):
                errors.append(f"{f['label']} is required.")
            data[key] = val
        if "slug" in data and not data["slug"] and res.get("slug_from"):
            data["slug"] = slugify(str(data.get(res["slug_from"], "")))
        if "published_at" in data and not data["published_at"]:
            data.pop("published_at")
        if "created_at" in data and not data["created_at"]:
            data.pop("created_at")
        if errors:
            for e in errors:
                flash(e, "danger")
            values.update(data)
        else:
            try:
                if row:
                    update(res["table"], row_id, data)
                else:
                    row_id = insert(res["table"], data)
                flash(f"{res['singular']} saved.", "success")
                return redirect(url_for("admin.edit_view", name=name, row_id=row_id))
            except Exception as exc:  # e.g. duplicate slug
                flash(f"Could not save: {exc}", "danger")
                values.update(data)

    extra = {}
    if name == "bookings" and row:
        extra["items"] = query("SELECT * FROM booking_items WHERE booking_id = ?", (row_id,))
    if name == "listings" and row:
        extra["view_url"] = url_for("public.detail", prefix=KINDS[row["kind"]]["prefix"], slug=row["slug"])
        extra["rooms"] = query("SELECT * FROM rooms WHERE listing_id = ?", (row_id,))
    if name in ("posts", "pages") and row:
        extra["view_url"] = url_for("public.page_or_post", slug=row["slug"])
    return render_template("admin/form.html", name=name, res=res, row=row, values=values,
                           fields=[{**f, "options": _choices(f)} for f in res["fields"]], **extra)


@bp.post("/<name>/<int:row_id>/delete/")
@admin_required
def delete_view(name, row_id):
    res = _resource(name)
    execute(f"DELETE FROM {res['table']} WHERE id = ?", (row_id,))
    flash(f"{res['singular']} deleted.", "success")
    return redirect(url_for("admin.list_view", name=name))


@bp.post("/reviews/<int:row_id>/approve/")
@admin_required
def approve_review(row_id):
    execute("UPDATE reviews SET approved = 1 WHERE id = ?", (row_id,))
    flash("Review approved.", "success")
    return redirect(request.referrer or url_for("admin.dashboard"))


# ------------------------------------------------------------------ settings & tools
@bp.route("/settings/", methods=["GET", "POST"])
@admin_required
def settings():
    if request.method == "POST":
        for key in DEFAULT_SETTINGS:
            if key in request.form:
                set_setting(key, request.form[key].strip())
        flash("Settings saved.", "success")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html", values=get_settings(), keys=list(DEFAULT_SETTINGS))


@bp.route("/subscribers.csv")
@admin_required
def subscribers_csv():
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["email", "subscribed"])
    for r in query("SELECT email, created_at FROM subscribers ORDER BY created_at"):
        w.writerow([r["email"], r["created_at"]])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=subscribers.csv"})


ALLOWED_IMAGES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


def save_upload(file_storage):
    ext = Path(file_storage.filename).suffix.lower()
    if ext not in ALLOWED_IMAGES:
        flash("Only image files can be uploaded.", "danger")
        return None
    name = f"{secrets.token_hex(4)}-{secure_filename(Path(file_storage.filename).stem)[:60]}{ext}"
    folder = Path(current_app.config["UPLOAD_FOLDER"])
    file_storage.save(os.fspath(folder / name))
    return url_for("static", filename=f"uploads/{name}")
