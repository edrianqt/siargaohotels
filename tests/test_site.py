"""Smoke tests: every public page renders, booking + admin flows work.

Run:  python -m pytest -q      (or simply: python tests/test_site.py)
"""
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from siargao import create_app  # noqa: E402
from siargao.db import init_db  # noqa: E402
from siargao.seed import run_seed  # noqa: E402


def make_client():
    tmp = tempfile.mkdtemp()
    app = create_app({"DATABASE": f"{tmp}/test.sqlite3", "TESTING": True})
    with app.app_context():
        init_db()
        run_seed()
    return app, app.test_client()


def token(client, url="/"):
    html = client.get(url).get_data(as_text=True)
    return re.search(r'name="_csrf" value="([^"]+)"', html).group(1)


def test_public_pages():
    _app, c = make_client()
    urls = ["/", "/hotels/", "/tours/", "/rentals/", "/car-and-motorcycle-rentals/",
            "/car-and-motorcycle-rentals/page/2/", "/hotels/?sort=price_asc&rating=excellent",
            "/tours/?category=joiner", "/car-and-motorcycle-rentals/?category=motorcycle&sort=name_desc",
            "/hotels/?location=socorro-siargao", "/st_hotel/isla-linaw-siargao/", "/st_hotel/cuadro-inn/",
            "/st_tour/sohoton-cove-joiner-tour/", "/st_car/toyota-vios-general-luna/",
            "/st_location/general-luna-siargao/", "/st_location/pilar-siargao/", "/blog/", "/category/things-to-do/",
            "/cloud-9-siargao/", "/about-us/", "/privacy-policy/", "/terms-and-conditions/", "/contact/",
            "/search?q=sohoton", "/login/", "/signup/", "/cart/", "/sitemap.xml", "/robots.txt",
            "/currency/USD", "/hotel_room/double-room-with-private-bathroom/"]
    for u in urls:
        r = c.get(u)
        assert r.status_code in (200, 301, 302), (u, r.status_code)
    assert c.get("/st_hotel/does-not-exist/").status_code == 404
    assert c.get("/nope-nope/").status_code == 404
    home = c.get("/").get_data(as_text=True)
    assert "Isla Linaw Siargao" in home and "Sohoton Cove Joiner Tour" in home
    assert "$" in home  # USD switch stuck in session


def test_filters():
    _app, c = make_client()
    moto = c.get("/car-and-motorcycle-rentals/?category=motorcycle").get_data(as_text=True)
    assert "Honda Beat" in moto and "Ford Ranger" not in moto
    gl = c.get("/hotels/?location=socorro-siargao").get_data(as_text=True)
    assert "Tiktikan" in gl and "Cuadro Inn" not in gl


def test_booking_flow():
    app, c = make_client()
    t = token(c, "/st_hotel/isla-linaw-siargao/")
    with app.app_context():
        from siargao.db import query
        lid = query("SELECT id FROM listings WHERE slug = 'isla-linaw-siargao'", one=True)["id"]
        rid = query("SELECT id FROM rooms WHERE listing_id = ?", (lid,), one=True)["id"]
    from datetime import date, timedelta
    s, e = date.today() + timedelta(days=10), date.today() + timedelta(days=13)
    # minimum-stay rule (2 nights) is enforced
    r = c.post("/cart/add", data={"_csrf": t, "listing_id": lid, "start": s.isoformat(),
                                  "end": (s + timedelta(days=1)).isoformat(), "adults": 2, "rooms": 1})
    assert r.status_code == 302 and "/st_hotel/" in r.headers["Location"]
    r = c.post("/cart/add", data={"_csrf": t, "listing_id": lid, "room_id": rid, "start": s.isoformat(),
                                  "end": e.isoformat(), "adults": 2, "rooms": 1}, follow_redirects=True)
    page = r.get_data(as_text=True)
    assert "₱4,350" in page, "3 nights × ₱1,450"
    r = c.post("/cart/checkout/", data={"_csrf": t, "name": "Juan Dela Cruz", "email": "juan@example.com",
                                        "phone": "09170000000", "accept": "1"}, follow_redirects=True)
    assert "Thank you, Juan" in r.get_data(as_text=True)


def test_csrf_required():
    _app, c = make_client()
    assert c.post("/contact/", data={"name": "x", "email": "x@y.z", "message": "hi"}).status_code == 400


def test_contact_review_subscribe_and_admin():
    app, c = make_client()
    t = token(c, "/contact/")
    assert c.post("/contact/", data={"_csrf": t, "name": "Ana", "email": "ana@example.com", "message": "Hello"},
                  follow_redirects=True).status_code == 200
    c.post("/subscribe", data={"_csrf": t, "email": "fan@example.com"})
    c.post("/st_hotel/cuadro-inn/review", data={"_csrf": t, "name": "Ben", "body": "Lovely stay", "title": "Great"})

    from werkzeug.security import generate_password_hash
    with app.app_context():
        from siargao.db import insert
        insert("users", {"email": "admin@example.com", "name": "Admin", "is_admin": 1,
                         "password_hash": generate_password_hash("secret123")})
    assert c.get("/admin/").status_code == 302  # not logged in
    t = token(c, "/login/")
    c.post("/login/", data={"_csrf": t, "email": "admin@example.com", "password": "secret123"})
    dash = c.get("/admin/").get_data(as_text=True)
    assert "Reviews waiting" in dash and "Ben" in dash
    for name in ["listings", "rooms", "reviews", "locations", "posts", "categories", "pages", "faqs",
                 "bookings", "messages", "subscribers", "users"]:
        assert c.get(f"/admin/{name}/").status_code == 200, name
    assert c.get("/admin/listings/3/edit/").status_code == 200
    assert c.get("/admin/listings/new/?kind=rental").status_code == 200
    assert c.get("/admin/settings/").status_code == 200
    assert "fan@example.com" in c.get("/admin/subscribers.csv").get_data(as_text=True)
    # create a rental from the admin and see it on the site
    t = token(c, "/admin/listings/new/?kind=rental")
    r = c.post("/admin/listings/new/", data={"_csrf": t, "kind": "rental", "title": "Beachfront Villa Test",
                                             "price": "5500", "price_unit": "night", "published": "on", "seats": "6"})
    assert r.status_code == 302
    assert "Beachfront Villa Test" in c.get("/rentals/").get_data(as_text=True)
    assert c.get("/st_rental/beachfront-villa-test/").status_code == 200


def test_pricing_rules():
    from siargao.helpers import price_line
    app, _c = make_client()
    with app.app_context():
        from siargao.db import query
        get = lambda slug: dict(query("SELECT * FROM listings WHERE slug = ?", (slug,), one=True))
        # private tour: 2 guests on a tour priced from 4 pax -> billed as 4 x 3998
        qty, unit, sub, _ = price_line(get("siargao-tri-island-corregidor-island-private-tour"), adults=2)
        assert (qty, unit, sub) == (4, 3998, 15992)
        # private tour: 6 guests -> 6 x 2998
        assert price_line(get("siargao-private-land-tour"), adults=6)[2] == 6 * 2998
        # joiner tour: flat per person
        assert price_line(get("sohoton-cove-joiner-tour"), adults=3)[2] == 3 * 2699
        # scooter: 4 days -> 3-6 day rate
        assert price_line(get("honda-beat-general-luna"), start="2027-01-01", end="2027-01-05")[2] == 4 * 420
        # car without tiers
        assert price_line(get("toyota-vios-general-luna"), start="2027-01-01", end="2027-01-03")[2] == 2 * 2100


def test_content_and_photos():
    _app, c = make_client()
    tour = c.get("/st_tour/sohoton-cove-private-tour/").get_data(as_text=True)
    assert "Inclusions" in tour and "Rates by group size" in tour and "Hagukan-Cave" in tour
    pkg = c.get("/st_tour/3d2n-all-inclusive-package/").get_data(as_text=True)
    assert "Itinerary" in pkg and "Day 2" in pkg
    beat = c.get("/st_car/honda-beat-general-luna/").get_data(as_text=True)
    assert "Rates by rental length" in beat and "Free Cancellation" in beat and "Rental requirements" in beat
    cuadro = c.get("/st_hotel/cuadro-inn/").get_data(as_text=True)
    assert "Quadruple Room" in cuadro and "Price on request" in cuadro and "Cuadro-Inn-Homestay-6" in cuadro
    assert c.get("/st_car/nissan-terra-sayak-airport/").status_code == 200
    assert "Pacifico" in c.get("/st_location/san-isidro-siargao/").get_data(as_text=True)
    blog = c.get("/blog/").get_data(as_text=True) + c.get("/blog/page/2/").get_data(as_text=True) \
        + c.get("/blog/page/3/").get_data(as_text=True)
    assert blog.count('class="card post-card') == 22
    assert c.get("/the-siargao-curse-whats-behind-the-islands-spell/").status_code == 200
    cars = c.get("/car-and-motorcycle-rentals/page/2/").get_data(as_text=True)
    assert "3 cars" not in cars and "Nissan" in cars


def test_unpriced_room_books_at_standard_rate():
    app, c = make_client()
    from datetime import date, timedelta
    with app.app_context():
        from siargao.db import query
        h = query("SELECT id FROM listings WHERE slug = 'cuadro-inn'", one=True)["id"]
        r = query("SELECT id FROM rooms WHERE listing_id = ? LIMIT 1", (h,), one=True)["id"]
    t = token(c, "/st_hotel/cuadro-inn/")
    s = date.today() + timedelta(days=5)
    page = c.post("/cart/add", data={"_csrf": t, "listing_id": h, "room_id": r, "start": s.isoformat(),
                                     "end": (s + timedelta(days=2)).isoformat(), "adults": 2, "rooms": 1},
                  follow_redirects=True).get_data(as_text=True)
    assert "₱2,400" in page  # 2 nights x ₱1,200 standard rate


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("✓", name)
