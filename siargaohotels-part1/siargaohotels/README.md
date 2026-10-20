# SiargaoHotels.ph — Python rebuild

A Python (Flask + SQLite) replacement for the WordPress / Traveler-theme site at
https://siargaohotels.ph. Same pages, same URLs, same content — plus its own admin
dashboard in place of wp-admin.

## What's included

| WordPress feature | Here |
|---|---|
| Home page (hero search with Hotel / Tours / Rental / Cars tabs, Book Now tiles, "We Live Here" story, hotel & tour grids, FAQs, travel tips) | `templates/home.html` |
| Hotels / Tours / Rentals / Cars archives with price, review-score & category filters, sorting, pagination | `/hotels/`, `/tours/`, `/rentals/`, `/car-and-motorcycle-rentals/` |
| Listing pages: gallery, description, facilities, rules & policies, rooms, map, reviews with sub-scores, booking box + inquiry tab, owner box, nearby listings | `/st_hotel/<slug>/`, `/st_tour/…`, `/st_rental/…`, `/st_car/…` |
| Locations menu (General Luna, Dapa, Socorro, Del Carmen, Pilar, San Isidro) | `/st_location/<slug>/` |
| Cart & checkout (min-stay rule, per-night / per-person / per-day / flat private-tour pricing) | `/cart/` → booking request with reference number + emails |
| Login / Sign up / My bookings | `/login/`, `/signup/`, `/account/` |
| Blog, categories, posts, pages (About, Privacy, Terms) | `/blog/`, `/category/<slug>/`, `/<slug>/` |
| Contact form, newsletter signup, PHP ⇄ USD switch, social links | footer + `/contact/` |
| SEO: canonical, Open Graph, meta descriptions, `sitemap.xml`, `robots.txt` | built in |
| wp-admin | `/admin/` — listings, rooms, reviews (approve), locations, bookings, messages, subscribers (CSV export), posts, pages, FAQs, users, site settings, image uploads |

All old URLs are kept, so Google rankings and shared links carry over.
Forms are protected with CSRF tokens and honeypots; passwords are hashed.

### Content already loaded by `flask seed`

Everything published on siargaohotels.ph as of October 2026:

- **7 hotels** — photo galleries, facilities, check-in/out rules, policies, 11 room types, ratings
- **8 tours** — galleries, highlights, itineraries, inclusions/exclusions, reminders, pick-up times,
  and per-group-size rates for private tours (the cart prices bookings by group size)
- **15 cars & motorcycles** — galleries, seats, transmission, multi-day scooter rates, deposits,
  delivery fees, rental requirements
- **6 locations** with photos, **22 blog posts** with featured images and categories,
  **8 FAQs**, the About page and the cars page text — about 160 photos in all

Listing descriptions and blog posts are short write-ups; `flask import-wp` swaps in your original
WordPress text. Room prices that were hidden behind "Show Price" on the old site show as
"Price on request" (guests book at the standard rate) — add them in **Admin → Hotel rooms**.
The Privacy Policy, Terms and Partner Policy pages are filled by `import-wp`.

**All 198 photos are bundled** in `siargao/static/uploads/wp/` (33 MB, same year/month folders as
WordPress). The site serves these local copies automatically, so nothing depends on the old
WordPress server. To pick up photos added to WordPress later, run `python tools/bundle_media.py`.

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                     # then edit SECRET_KEY etc.

flask --app wsgi seed                                    # create DB + load the site's content and photos
flask --app wsgi import-wp                               # pull full blog posts & pages from WordPress
flask --app wsgi create-admin                            # your admin login
flask --app wsgi run --debug                             # http://127.0.0.1:5000
```

Run the tests with `python tests/test_site.py` (or `pytest`).

## Moving off WordPress

1. `flask --app wsgi import-wp` — imports posts, pages and categories through the public
   WordPress REST API. If the Traveler post types are exposed in the API, new listings are
   added as drafts (set their price and publish them in the admin).
2. Photos are already bundled. If `import-wp` brings in articles with extra images, run
   `flask --app wsgi download-media` while WordPress is still online to copy those too.
3. Fill in the hidden room prices in `/admin/`. Upgrading an existing database? Run
   `flask --app wsgi seed --refresh` to load the new content over it.

## Deploy (any Linux VPS)

```bash
pip install -r requirements.txt
gunicorn -w 3 -b 127.0.0.1:8000 wsgi:app
```

Put Nginx in front (proxy to port 8000, serve `/static/` directly), add HTTPS with
Let's Encrypt, and set `SESSION_COOKIE_SECURE=1`. Back up `instance/siargao.sqlite3` and
`siargao/static/uploads/` regularly. SQLite comfortably handles a site of this size; the data
layer in `siargao/db.py` is small if you later want to move to PostgreSQL.

## Not carried over yet

- Online payment (bookings are requests that you confirm; add PayMongo/PayPal at checkout when ready)
- Google sign-in and password-reset emails
- Live availability calendars per room / vehicle

## Project layout

```
wsgi.py                 entry point (flask / gunicorn)
siargao/__init__.py     app factory + CLI commands (seed, import-wp, download-media, create-admin)
siargao/schema.sql      database tables
siargao/views/          public.py · cart.py · auth.py · admin.py
siargao/templates/      Jinja templates (site + admin)
siargao/static/         css, js, uploads
siargao/seed.py         content copied from the live site
siargao/wp_import.py    WordPress REST importer + media downloader
tests/test_site.py      smoke tests for every page and the booking/admin flows
```
