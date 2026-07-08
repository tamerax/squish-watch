"""
Simple SQLite-backed 'seen it already' tracker so we don't spam
notifications for the same listing every poll cycle.
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent / "seen.sqlite3"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS seen_listings (
            source TEXT NOT NULL,
            listing_id TEXT NOT NULL,
            item_name TEXT,
            title TEXT,
            url TEXT,
            first_seen_utc TEXT,
            PRIMARY KEY (source, listing_id)
        )
        """
    )
    conn.commit()
    return conn


def is_new(conn, source: str, listing_id: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM seen_listings WHERE source = ? AND listing_id = ?",
        (source, listing_id),
    )
    return cur.fetchone() is None


def mark_seen(conn, source: str, listing_id: str, item_name: str, title: str, url: str):
    conn.execute(
        """
        INSERT OR IGNORE INTO seen_listings
        (source, listing_id, item_name, title, url, first_seen_utc)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (source, listing_id, item_name, title, url, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
