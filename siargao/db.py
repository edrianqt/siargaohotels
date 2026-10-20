"""Tiny SQLite data layer (stdlib only)."""
import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA = Path(__file__).with_name("schema.sql")


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


NEW_COLUMNS = {  # columns added after the first release; init_db adds any that are missing
    "listings": ["highlights", "itinerary", "inclusions", "exclusions", "reminders", "features",
                 "start_time", "rate_tiers"],
}


def init_db():
    db = get_db()
    db.executescript(SCHEMA.read_text())
    for table, cols in NEW_COLUMNS.items():
        have = {r[1] for r in db.execute(f"PRAGMA table_info({table})")}
        for col in cols:
            if col not in have:
                db.execute(f"ALTER TABLE {table} ADD COLUMN {col} TEXT DEFAULT ''")
    db.commit()


def query(sql, params=(), one=False):
    cur = get_db().execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute(sql, params=()):
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    return cur.lastrowid


def insert(table, data: dict):
    cols = ", ".join(data)
    marks = ", ".join("?" for _ in data)
    return execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})", tuple(data.values()))


def update(table, row_id, data: dict):
    sets = ", ".join(f"{k} = ?" for k in data)
    execute(f"UPDATE {table} SET {sets} WHERE id = ?", (*data.values(), row_id))


# ---- settings -------------------------------------------------------------
DEFAULT_SETTINGS = {
    "site_name": "Siargao Hotels",
    "tagline": "Your Siargao trip, booked with the people who live here.",
    "phone": "+639458259355",
    "email": "info@siargaohotels.ph",
    "address": "Burgos St, Brgy. Taruc, Socorro, Surigao del Norte",
    "operator": "IAO Booking Services",
    "facebook": "https://www.facebook.com/SiargaoHotels.ph",
    "instagram": "https://www.instagram.com/siargaohotels/",
    "tiktok": "https://www.tiktok.com/@siargaohotels",
    "logo_url": "https://siargaohotels.ph/wp-content/uploads/2026/01/Siargao-Hotels.png",
    "logo_white_url": "https://siargaohotels.ph/wp-content/uploads/2018/11/Siargao-Hotels-white-logo.png",
    "favicon_url": "https://siargaohotels.ph/wp-content/uploads/2025/11/Siargao-Hotels-favicon-270x270.png",
    "hero_image": "https://siargaohotels.ph/wp-content/uploads/2025/12/Cloud-9-Surfing-Area-Siargao.jpg",
    "php_per_usd": "58",
    "meta_description": (
        "SiargaoHotels.ph helps you discover the best hotels in General Luna Siargao Island "
        "and Cloud 9 Siargao hotels. Explore curated stays, from surf-friendly spots to luxury "
        "resorts and budget accommodations across Siargao."
    ),
}


def get_settings() -> dict:
    if "settings" not in g:
        s = dict(DEFAULT_SETTINGS)
        try:
            for r in query("SELECT key, value FROM settings"):
                s[r["key"]] = r["value"]
        except sqlite3.OperationalError:
            pass
        g.settings = s
    return g.settings


def set_setting(key, value):
    execute(
        "INSERT INTO settings(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
