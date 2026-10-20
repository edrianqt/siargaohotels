"""Shared helpers: listing types, ratings, prices, CSRF, auth guards."""
import re
import secrets
import unicodedata
from datetime import date, datetime
from functools import wraps

from flask import abort, flash, g, redirect, request, session, url_for

from .db import get_settings, query

# Product types, their WordPress-compatible URL prefixes and archive pages.
KINDS = {
    "hotel": {"label": "Hotel", "plural": "Hotels", "prefix": "st_hotel",
              "archive": "hotels", "unit": "night"},
    "tour": {"label": "Tour", "plural": "Tours", "prefix": "st_tour",
             "archive": "tours", "unit": "person"},
    "rental": {"label": "Rental", "plural": "Rentals", "prefix": "st_rental",
               "archive": "rentals", "unit": "night"},
    "car": {"label": "Car", "plural": "Cars/Motorcycles", "prefix": "st_car",
            "archive": "car-and-motorcycle-rentals", "unit": "day"},
}
PREFIX_TO_KIND = {v["prefix"]: k for k, v in KINDS.items()}
ARCHIVE_TO_KIND = {v["archive"]: k for k, v in KINDS.items()}

CATEGORIES = {
    "tour": [("joiner", "Joiner Tour"), ("private", "Private Tour")],
    "car": [("car", "Car"), ("motorcycle", "Motorcycle")],
}

REVIEW_ASPECTS = [
    ("cleanliness", "Cleanliness"), ("comfort", "Comfort"), ("location", "Location"),
    ("facilities", "Facilities"), ("staff", "Staff"), ("value", "Value For Money"),
]

RATING_BANDS = [  # (min score, label, filter key)
    (4.5, "Excellent", "excellent"),
    (4.0, "Very Good", "very_good"),
    (3.0, "Average", "average"),
    (2.0, "Poor", "poor"),
    (0.01, "Terrible", "terrible"),
]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s_]+", "-", text) or secrets.token_hex(3)


def rating_label(score) -> str:
    score = float(score or 0)
    for floor, label, _ in RATING_BANDS:
        if score >= floor:
            return label
    return "Not Rated"


def listing_stats(listing_id: int, imported_rating=0, imported_reviews=0):
    """Average rating + count; approved reviews in the DB win over imported stats."""
    row = query(
        "SELECT COUNT(*) n, AVG((cleanliness+comfort+location+facilities+staff+value)/6.0) avg "
        "FROM reviews WHERE listing_id = ? AND approved = 1",
        (listing_id,), one=True,
    )
    if row["n"]:
        return round(row["avg"], 1), row["n"]
    return round(imported_rating or 0, 1), imported_reviews or 0


def enrich(rows):
    """Turn sqlite rows into dicts with rating + url info for templates."""
    out = []
    for r in rows:
        d = dict(r)
        d["rating"], d["review_count"] = listing_stats(d["id"], d.get("imported_rating"), d.get("imported_reviews"))
        d["rating_label"] = rating_label(d["rating"])
        d["url"] = url_for("public.detail", prefix=KINDS[d["kind"]]["prefix"], slug=d["slug"])
        d["gallery_list"] = [u.strip() for u in (d.get("gallery") or "").splitlines() if u.strip()]
        out.append(d)
    return out


def parse_facilities(text: str):
    """'Group: a, b' lines -> [(group, [a, b])]."""
    groups = []
    for line in (text or "").splitlines():
        if ":" in line:
            name, items = line.split(":", 1)
            groups.append((name.strip(), [i.strip() for i in items.split(",") if i.strip()]))
        elif line.strip():
            groups.append(("Facilities", [i.strip() for i in line.split(",") if i.strip()]))
    return groups


# ---- money ---------------------------------------------------------------
def current_currency():
    return session.get("currency", "PHP")


def money(amount, decimals=None):
    amount = float(amount or 0)
    if current_currency() == "USD":
        rate = float(get_settings().get("php_per_usd") or 58)
        return f"${amount / rate:,.2f}"
    return f"₱{amount:,.0f}" if decimals is None else f"₱{amount:,.{decimals}f}"


# ---- dates & pricing ----------------------------------------------------------
def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def parse_tiers(text):
    """'4: 3998' lines (or comma separated) -> sorted [(4, 3998.0), ...]."""
    tiers = []
    for part in re.split(r"[\n,;]+", text or ""):
        m = re.match(r"\s*(\d+)\s*\+?\s*(?:pax|days?)?\s*[:=]\s*₱?\s*([\d,.]+)", part)
        if m:
            tiers.append((int(m.group(1)), float(m.group(2).replace(",", ""))))
    return sorted(tiers)


def tier_price(tiers, n):
    """Price for the highest tier threshold <= n. Below the first tier, the first tier
    applies and n is raised to its minimum (e.g. a private boat priced from 4 pax)."""
    if not tiers:
        return None, n
    if n < tiers[0][0]:
        return tiers[0][1], tiers[0][0]
    return [p for t, p in tiers if t <= n][-1], n


def price_line(listing, room=None, start=None, end=None, adults=1, children=0, rooms=1):
    """Return (quantity, unit_price, subtotal, description) for a cart line."""
    unit = room["price"] if room and room["price"] else listing["price"]
    s, e = parse_date(start), parse_date(end)
    tiers = parse_tiers(listing.get("rate_tiers"))
    if listing["kind"] in ("hotel", "rental"):
        nights = max((e - s).days, 1) if s and e else 1
        nights = max(nights, listing.get("min_stay") or 1)
        qty = nights * (rooms if listing["kind"] == "hotel" else 1)
        desc = f"{nights} night(s)" + (f" × {rooms} room(s)" if listing["kind"] == "hotel" else "")
    elif listing["kind"] == "car":
        days = max((e - s).days, 1) if s and e else 1
        if tiers:
            unit = tier_price(tiers, days)[0]
        qty, desc = days, f"{days} day(s)"
    else:  # tours
        guests = max(adults + children, 1)
        if tiers:  # private tours: per-person rate depends on group size
            unit, qty = tier_price(tiers, guests)
            desc = f"{guests} guest(s), group rate" + (f" (minimum {qty} pax)" if qty > guests else "")
        else:      # joiner tours: flat per person
            qty, desc = guests, f"{guests} guest(s)"
    return qty, unit, qty * unit, desc


# ---- CSRF ----------------------------------------------------------------
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


def csrf_protect():
    if request.method == "POST":
        sent = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
        if not sent or sent != session.get("_csrf"):
            abort(400, "Invalid or missing form token. Please reload the page and try again.")


# ---- auth guards -----------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not g.user:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.full_path))
        return view(*a, **kw)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not g.user:
            return redirect(url_for("auth.login", next=request.full_path))
        if not g.user["is_admin"]:
            abort(403)
        return view(*a, **kw)
    return wrapped


def today_iso(offset=0):
    from datetime import timedelta
    return (date.today() + timedelta(days=offset)).isoformat()
