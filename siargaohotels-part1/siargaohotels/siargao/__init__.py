"""SiargaoHotels.ph — Python (Flask) rebuild of the WordPress/Traveler site."""
import os
import re
from urllib.parse import quote
from pathlib import Path

import click
from flask import Flask, g, render_template, request, session

from . import db as dbmod
from .helpers import (CATEGORIES, KINDS, csrf_protect, csrf_token, current_currency,
                      money, parse_tiers, rating_label, today_iso)

BASE_DIR = Path(__file__).resolve().parent.parent


def create_app(test_config=None):
    app = Flask(__name__, instance_path=str(BASE_DIR / "instance"))
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-change-me"),
        DATABASE=os.environ.get("DATABASE_PATH", str(BASE_DIR / "instance" / "siargao.sqlite3")),
        UPLOAD_FOLDER=str(Path(__file__).parent / "static" / "uploads"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "0") == "1",
        MAIL_SERVER=os.environ.get("MAIL_SERVER", ""),
        MAIL_PORT=int(os.environ.get("MAIL_PORT", "587")),
        MAIL_USERNAME=os.environ.get("MAIL_USERNAME", ""),
        MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", ""),
        MAIL_FROM=os.environ.get("MAIL_FROM", "info@siargaohotels.ph"),
        ADMIN_NOTIFY=os.environ.get("ADMIN_NOTIFY", "info@siargaohotels.ph"),
        PER_PAGE=12,
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(dbmod.close_db)

    @app.before_request
    def load_user_and_check_csrf():
        g.user = None
        uid = session.get("user_id")
        if uid:
            g.user = dbmod.query("SELECT * FROM users WHERE id = ?", (uid,), one=True)
        csrf_protect()

    @app.context_processor
    def inject_globals():
        cart = session.get("cart", [])
        return {
            "S": dbmod.get_settings(),
            "KINDS": KINDS,
            "CATEGORIES": CATEGORIES,
            "nav_locations": dbmod.query("SELECT slug, name FROM locations ORDER BY position, name"),
            "cart_count": len(cart),
            "currency": current_currency(),
            "csrf_token": csrf_token,
            "today": today_iso,
        }

    register_local_media(app)

    app.jinja_env.filters["money"] = money
    app.jinja_env.filters["rating_label"] = rating_label
    app.jinja_env.filters["tiers"] = parse_tiers
    app.jinja_env.filters["lines"] = lambda t: [ln.strip(" -•\t") for ln in (t or "").splitlines() if ln.strip(" -•\t")]

    from .views.public import bp as public_bp
    from .views.auth import bp as auth_bp
    from .views.cart import bp as cart_bp
    from .views.admin import bp as admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(public_bp)  # last: owns the WordPress-style catch-all /<slug>/

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("errors/error.html", code=403, message="You don't have access to this page."), 403

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/error.html", code=400, message=getattr(e, "description", "Bad request")), 400

    register_cli(app)
    return app


WP_MEDIA = re.compile(r"https?://(?:www\.)?siargaohotels\.ph/wp-content/uploads/([\w\-./%]+?\.(?:jpe?g|png|gif|webp|svg))",
                      re.IGNORECASE)


def register_local_media(app):
    """Serve bundled copies of old WordPress photos (static/uploads/wp/...) instead of hot-linking them.

    Any siargaohotels.ph/wp-content/uploads URL in a page is rewritten to the local file when it exists,
    so content in the database never needs editing. Missing files keep their original URL.
    """
    root = Path(app.static_folder) / "uploads" / "wp"
    seen = {}

    def exists(rel):
        if rel not in seen:
            seen[rel] = (root / rel).is_file()
        return seen[rel]

    def local(match):
        rel = match.group(1)
        return f"/static/uploads/wp/{rel}" if exists(rel) else match.group(0)

    sized = re.compile(r"^(?P<stem>.+)-\d+x\d+(?P<ext>\.(?:jpe?g|png|webp))$", re.IGNORECASE)

    @app.template_filter("full")
    def full_size(url):
        """Swap a WordPress thumbnail (photo-931x594.jpg) for the bundled full-size photo when we have it.
        Used where photos display large: hero, galleries, lightbox, location and blog headers."""
        if not url:
            return url
        m = re.search(r"(?:/wp-content/uploads/|/static/uploads/wp/)(.+)$", url)
        if not m:
            return url
        rel = m.group(1)
        o = sized.match(rel)
        if o and exists(o.group("stem") + o.group("ext")):
            return f"/static/uploads/wp/{o.group('stem')}{o.group('ext')}"
        return url

    @app.after_request
    def rewrite_media(response):
        if response.mimetype in ("text/html", "application/xml") and not response.direct_passthrough \
                and root.is_dir():
            body = response.get_data(as_text=True)
            if "wp-content/uploads" in body:
                base = request.url_root.rstrip("/")

                def absolute(m):  # og:image and sitemap need full URLs
                    rel = m.group(2)
                    return m.group(1) + (f"{base}/static/uploads/wp/{rel}" if exists(rel) else m.group(0)[len(m.group(1)):])

                def encoded(m):   # share links carry the image URL url-encoded
                    rel = m.group(1)
                    return quote(f"{base}/static/uploads/wp/{rel}", safe="/") if exists(rel) else m.group(0)

                body = re.sub(r'(<meta property="og:image" content=")https?://(?:www\.)?siargaohotels\.ph/wp-content/uploads/([^"]+)',
                              absolute, body)
                body = re.sub(r"https?%3A//(?:www\.)?siargaohotels\.ph/wp-content/uploads/([\w\-./%]+?\.(?:jpe?g|png|gif|webp))",
                              encoded, body, flags=re.IGNORECASE)
                response.set_data(WP_MEDIA.sub(local, body))
        return response


def register_cli(app):
    @app.cli.command("init-db")
    def init_db_cmd():
        """Create tables."""
        dbmod.init_db()
        click.echo("Database ready.")

    @app.cli.command("seed")
    @click.option("--refresh", is_flag=True, help="Overwrite existing listings/posts/pages with the bundled content.")
    def seed_cmd(refresh):
        """Load the listings, photos, FAQs, blog and pages from siargaohotels.ph."""
        from .seed import run_seed
        dbmod.init_db()
        run_seed(refresh=refresh)
        click.echo("Seeded content." + (" Existing records refreshed." if refresh else ""))

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--name", prompt=True, default="Admin")
    @click.password_option()
    def create_admin(email, name, password):
        """Create (or promote) an admin user."""
        from werkzeug.security import generate_password_hash
        existing = dbmod.query("SELECT id FROM users WHERE email = ?", (email.lower(),), one=True)
        if existing:
            dbmod.update("users", existing["id"], {"is_admin": 1, "password_hash": generate_password_hash(password)})
        else:
            dbmod.insert("users", {"email": email.lower(), "name": name,
                                   "password_hash": generate_password_hash(password), "is_admin": 1})
        click.echo(f"Admin ready: {email}")

    @app.cli.command("import-wp")
    @click.option("--site", default="https://siargaohotels.ph")
    @click.option("--listings/--no-listings", default=True, help="Also try Traveler post types.")
    def import_wp(site, listings):
        """Import posts, pages, categories (and listings if exposed) from the WordPress REST API."""
        from .wp_import import run_import
        dbmod.init_db()
        run_import(site.rstrip("/"), include_listings=listings, echo=click.echo)

    @app.cli.command("download-media")
    @click.option("--host", default="siargaohotels.ph")
    def download_media(host):
        """Copy every image still hot-linked from the old WordPress site into static/uploads."""
        from .wp_import import localize_media
        localize_media(host, echo=click.echo)
