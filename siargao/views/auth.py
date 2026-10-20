"""Login, sign up, logout and the customer account page."""
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import insert, query
from ..helpers import login_required

bp = Blueprint("auth", __name__)


def _safe_next(default):
    nxt = request.values.get("next", "")
    return nxt if nxt.startswith("/") and not nxt.startswith("//") else default


@bp.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = query("SELECT * FROM users WHERE email = ?", (email,), one=True)
        if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
            session.clear()
            session["user_id"] = user["id"]
            session.permanent = bool(request.form.get("remember"))
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(_safe_next(url_for("admin.dashboard") if user["is_admin"] else url_for("auth.account")))
        flash("Incorrect email or password.", "danger")
    return render_template("auth/login.html")


@bp.route("/signup/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        f = request.form
        email, name, pw = f.get("email", "").strip().lower(), f.get("name", "").strip(), f.get("password", "")
        if not name or "@" not in email or len(pw) < 8:
            flash("Enter your name, a valid email and a password of at least 8 characters.", "danger")
        elif not f.get("accept"):
            flash("Please accept the Terms and Privacy Policy.", "danger")
        elif query("SELECT id FROM users WHERE email = ?", (email,), one=True):
            flash("An account with that email already exists.", "warning")
        else:
            uid = insert("users", {"email": email, "name": name, "password_hash": generate_password_hash(pw)})
            session.clear()
            session["user_id"] = uid
            flash("Your account is ready.", "success")
            return redirect(_safe_next(url_for("auth.account")))
    return render_template("auth/signup.html")


@bp.route("/logout/")
def logout():
    cart, currency = session.get("cart"), session.get("currency")
    session.clear()
    if cart:
        session["cart"] = cart
    if currency:
        session["currency"] = currency
    return redirect(url_for("public.home"))


@bp.route("/account/")
@login_required
def account():
    bookings = query("SELECT * FROM bookings WHERE user_id = ? OR email = ? ORDER BY created_at DESC",
                     (g.user["id"], g.user["email"]))
    return render_template("auth/account.html", bookings=bookings)
