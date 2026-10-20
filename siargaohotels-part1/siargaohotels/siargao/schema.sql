-- SiargaoHotels.ph database schema (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS locations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slug        TEXT UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    zipcode     TEXT DEFAULT '',
    description TEXT DEFAULT '',
    image_url   TEXT DEFAULT '',
    position    INTEGER DEFAULT 0
);

-- One table for every bookable product, like WordPress post types
-- (st_hotel, st_tour, st_rental, st_car).
CREATE TABLE IF NOT EXISTS listings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    kind            TEXT NOT NULL CHECK (kind IN ('hotel','tour','rental','car')),
    slug            TEXT NOT NULL,
    title           TEXT NOT NULL,
    location_id     INTEGER REFERENCES locations(id) ON DELETE SET NULL,
    address         TEXT DEFAULT '',
    summary         TEXT DEFAULT '',
    description     TEXT DEFAULT '',          -- HTML
    image_url       TEXT DEFAULT '',
    gallery         TEXT DEFAULT '',          -- one image URL per line
    price           REAL DEFAULT 0,
    price_unit      TEXT DEFAULT 'night',     -- night | person | day | booking
    category        TEXT DEFAULT '',          -- tours: joiner/private ; cars: car/motorcycle
    duration        TEXT DEFAULT '',          -- tours
    seats           INTEGER DEFAULT 0,        -- cars / rentals (max guests)
    transmission    TEXT DEFAULT '',          -- cars
    bedrooms        INTEGER DEFAULT 0,        -- rentals
    phone           TEXT DEFAULT '',
    facilities      TEXT DEFAULT '',          -- "Group: item, item" per line
    check_in        TEXT DEFAULT '',
    check_out       TEXT DEFAULT '',
    policies        TEXT DEFAULT '',          -- HTML
    min_stay        INTEGER DEFAULT 1,
    owner_name      TEXT DEFAULT '',
    highlights      TEXT DEFAULT '',          -- one per line
    itinerary       TEXT DEFAULT '',          -- "Day 1: ..." one per line
    inclusions      TEXT DEFAULT '',          -- one per line
    exclusions      TEXT DEFAULT '',          -- one per line
    reminders       TEXT DEFAULT '',          -- one per line
    features        TEXT DEFAULT '',          -- badges, comma separated
    start_time      TEXT DEFAULT '',
    rate_tiers      TEXT DEFAULT '',          -- tours: "4: 3998" (guests: price/person); vehicles: "3: 495" (days: price/day)
    map_query       TEXT DEFAULT '',
    imported_rating REAL DEFAULT 0,           -- rating carried over from WordPress
    imported_reviews INTEGER DEFAULT 0,
    featured        INTEGER DEFAULT 0,
    published       INTEGER DEFAULT 1,
    seo_title       TEXT DEFAULT '',
    seo_description TEXT DEFAULT '',
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE (kind, slug)
);

CREATE TABLE IF NOT EXISTS rooms (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    slug       TEXT DEFAULT '',
    name       TEXT NOT NULL,
    size_m2    INTEGER DEFAULT 0,
    beds       INTEGER DEFAULT 1,
    max_adults INTEGER DEFAULT 2,
    price      REAL DEFAULT 0,
    image_url  TEXT DEFAULT '',
    description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS reviews (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id  INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    email       TEXT DEFAULT '',
    title       TEXT DEFAULT '',
    body        TEXT DEFAULT '',
    cleanliness REAL DEFAULT 5,
    comfort     REAL DEFAULT 5,
    location    REAL DEFAULT 5,
    facilities  REAL DEFAULT 5,
    staff       REAL DEFAULT 5,
    value       REAL DEFAULT 5,
    approved    INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    slug         TEXT UNIQUE NOT NULL,
    title        TEXT NOT NULL,
    excerpt      TEXT DEFAULT '',
    body         TEXT DEFAULT '',             -- HTML
    image_url    TEXT DEFAULT '',
    category_id  INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    published    INTEGER DEFAULT 1,
    published_at TEXT DEFAULT (datetime('now')),
    seo_description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS pages (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    slug  TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    body  TEXT DEFAULT '',
    seo_description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS faqs (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer   TEXT NOT NULL,                   -- HTML
    position INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT UNIQUE NOT NULL,
    name          TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin      INTEGER DEFAULT 0,
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bookings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ref        TEXT UNIQUE NOT NULL,
    user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL,
    phone      TEXT DEFAULT '',
    notes      TEXT DEFAULT '',
    total      REAL DEFAULT 0,
    status     TEXT DEFAULT 'pending',       -- pending | confirmed | cancelled | completed
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS booking_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id  INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    listing_id  INTEGER REFERENCES listings(id) ON DELETE SET NULL,
    room_id     INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
    title       TEXT NOT NULL,
    start_date  TEXT DEFAULT '',
    end_date    TEXT DEFAULT '',
    adults      INTEGER DEFAULT 1,
    children    INTEGER DEFAULT 0,
    quantity    REAL DEFAULT 1,
    unit_price  REAL DEFAULT 0,
    subtotal    REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL,
    phone      TEXT DEFAULT '',
    address    TEXT DEFAULT '',
    subject    TEXT DEFAULT '',
    message    TEXT NOT NULL,
    listing_id INTEGER REFERENCES listings(id) ON DELETE SET NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS subscribers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    email      TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_listings_kind ON listings(kind, published);
CREATE INDEX IF NOT EXISTS idx_reviews_listing ON reviews(listing_id, approved);
