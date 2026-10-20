"""Session cart, checkout and booking confirmation (replaces the Traveler/WooCommerce cart)."""
import secrets
from datetime import datetime

from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, session, url_for

from ..db import get_db, query
from ..helpers import KINDS, parse_date, price_line
from ..mailer import send_mail

bp = Blueprint("cart", __name__, url_prefix="/cart")


def _cart():
    return session.setdefault("cart", [])


def _lines():
    """Re-price every cart line from the database (never trust stored prices)."""
    lines, total = [], 0
    for idx, c in enumerate(_cart()):
        item = query("SELECT * FROM listings WHERE id = ? AND published = 1", (c["listing_id"],), one=True)
        if not item:
            continue
        item = dict(item)
        room = query("SELECT * FROM rooms WHERE id = ? AND listing_id = ?", (c.get("room_id"), item["id"]), one=True) \
            if c.get("room_id") else None
        qty, unit, sub, desc = price_line(item, room, c.get("start"), c.get("end"),
                                          c.get("adults", 1), c.get("children", 0), c.get("rooms", 1))
        total += sub
        lines.append({"idx": idx, "item": item, "room": room, "qty": qty, "unit": unit, "subtotal": sub,
                      "desc": desc, **c,
                      "url": url_for("public.detail", prefix=KINDS[item["kind"]]["prefix"], slug=item["slug"])})
    return lines, total


def _priced_room(listing_id, room_id):
    """Only rooms with a published price can be booked; others fall back to the standard rate."""
    if not room_id:
        return None
    room = query("SELECT id, price FROM rooms WHERE id = ? AND listing_id = ?", (room_id, listing_id), one=True)
    return room["id"] if room and room["price"] else None


@bp.post("/add")
def add():
    f = request.form
    item = query("SELECT * FROM listings WHERE id = ? AND published = 1", (f.get("listing_id", type=int),), one=True)
    if not item:
        abort(404)
    start, end = f.get("start", ""), f.get("end", "")
    back = url_for("public.detail", prefix=KINDS[item["kind"]]["prefix"], slug=item["slug"])
    s, e = parse_date(start), parse_date(end)
    if item["kind"] != "tour" and (not s or not e or e <= s):
        flash("Please choose valid dates (the end date must be after the start date).", "danger")
        return redirect(back)
    if s and s < datetime.now().date():
        flash("Dates in the past can't be booked.", "danger")
        return redirect(back)
    if item["kind"] in ("hotel", "rental") and (e - s).days < (item["min_stay"] or 1):
        flash(f"A minimum stay of {item['min_stay']} nights is required for this property.", "warning")
        return redirect(back)
    _cart().append({
        "listing_id": item["id"], "room_id": _priced_room(item["id"], f.get("room_id", type=int)),
        "start": start, "end": end if item["kind"] != "tour" else "",
        "adults": max(f.get("adults", 1, type=int), 1), "children": max(f.get("children", 0, type=int), 0),
        "rooms": max(f.get("rooms", 1, type=int), 1),
    })
    session.modified = True
    flash(f"{item['title']} was added to your cart.", "success")
    return redirect(url_for("cart.view"))


@bp.post("/remove/<int:idx>")
def remove(idx):
    cart = _cart()
    if 0 <= idx < len(cart):
        cart.pop(idx)
        session.modified = True
    return redirect(url_for("cart.view"))


@bp.route("/")
def view():
    lines, total = _lines()
    return render_template("cart/cart.html", lines=lines, total=total)


@bp.route("/checkout/", methods=["GET", "POST"])
def checkout():
    lines, total = _lines()
    if not lines:
        flash("Your cart is empty.", "info")
        return redirect(url_for("cart.view"))
    if request.method == "POST":
        f = request.form
        if not f.get("name") or "@" not in f.get("email", "") or not f.get("phone"):
            flash("Name, email and phone are required.", "danger")
            return render_template("cart/checkout.html", lines=lines, total=total, form=f)
        if not f.get("accept"):
            flash("Please accept the Terms & Conditions.", "danger")
            return render_template("cart/checkout.html", lines=lines, total=total, form=f)
        ref = "SH" + datetime.now().strftime("%y%m%d") + secrets.token_hex(3).upper()
        db = get_db()
        cur = db.execute(
            "INSERT INTO bookings(ref, user_id, name, email, phone, notes, total) VALUES (?,?,?,?,?,?,?)",
            (ref, g.user["id"] if g.user else None, f["name"], f["email"].lower(), f["phone"], f.get("notes", ""), total))
        bid = cur.lastrowid
        for ln in lines:
            title = ln["item"]["title"] + (f" — {ln['room']['name']}" if ln["room"] else "")
            db.execute(
                "INSERT INTO booking_items(booking_id, listing_id, room_id, title, start_date, end_date, adults, "
                "children, quantity, unit_price, subtotal) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (bid, ln["item"]["id"], ln["room"]["id"] if ln["room"] else None, title, ln["start"], ln["end"],
                 ln["adults"], ln["children"], ln["qty"], ln["unit"], ln["subtotal"]))
        db.commit()
        session["cart"] = []
        summary = "\n".join(f"- {ln['item']['title']} ({ln['desc']}) {ln['start']} {ln['end']}: ₱{ln['subtotal']:,.0f}"
                            for ln in lines)
        body = (f"Booking {ref}\n{f['name']} <{f['email']}> {f['phone']}\n\n{summary}\n\nTotal: ₱{total:,.0f}\n\n"
                f"Notes: {f.get('notes','')}")
        send_mail(current_app.config["ADMIN_NOTIFY"], f"New booking {ref}", body)
        send_mail(f["email"], f"Your Siargao Hotels booking request {ref}",
                  "Thank you! We received your booking request and will confirm availability shortly.\n\n" + body)
        session.setdefault("my_bookings", []).append(ref)
        session.modified = True
        return redirect(url_for("cart.confirmation", ref=ref))
    form = {"name": g.user["name"], "email": g.user["email"]} if g.user else {}
    return render_template("cart/checkout.html", lines=lines, total=total, form=form)


@bp.route("/booking/<ref>/")
def confirmation(ref):
    booking = query("SELECT * FROM bookings WHERE ref = ?", (ref,), one=True)
    if not booking:
        abort(404)
    allowed = ref in session.get("my_bookings", []) or (
        g.user and (g.user["is_admin"] or g.user["id"] == booking["user_id"]))
    if not allowed:
        abort(403)
    items = query("SELECT * FROM booking_items WHERE booking_id = ?", (booking["id"],))
    return render_template("cart/confirmation.html", booking=booking, items=items)
