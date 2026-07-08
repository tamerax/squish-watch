#!/usr/bin/env python3
"""
squish-watch: polls eBay, Reddit, Poshmark, and Mercari for specific
Squishable listings and pushes an ntfy.sh notification on new matches.

Run this on a cron schedule (see README.md). Each run is stateless except
for seen.sqlite3, which tracks what's already been notified.
"""
import sys
import traceback
from pathlib import Path

import yaml

import db
import notify
from sources.ebay import search_ebay
from sources.reddit import search_reddit
from sources.poshmark import search_poshmark
from sources.mercari import search_mercari
from sources.facebook import search_facebook

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def run_source(source_name, search_fn, item_name, search_term, conn, ntfy_topic):
    try:
        results = search_fn(search_term)
    except Exception as e:
        print(f"[{source_name}] ERROR searching '{search_term}': {e}")
        traceback.print_exc()
        return 0

    new_count = 0
    for r in results:
        listing_id = r.get("listing_id")
        if not listing_id:
            continue
        if db.is_new(conn, source_name, listing_id):
            db.mark_seen(conn, source_name, listing_id, item_name, r.get("title", ""), r.get("url", ""))
            new_count += 1

            price_str = f" - {r['price']}" if r.get("price") else ""
            notify.send_ntfy(
                topic=ntfy_topic,
                title=f"🧸 {item_name}",
                message=f"[{source_name}] {r.get('title', '(no title)')}{price_str}",
                url=r.get("url"),
            )
            print(f"[{source_name}] NEW MATCH: {r.get('title')} -> {r.get('url')}")

    return new_count


def main():
    cfg = load_config()
    ntfy_topic = cfg["ntfy"]["topic"]
    conn = db.get_conn()

    total_new = 0

    for item in cfg.get("items", []):
        item_name = item["name"]
        for term in item.get("search_terms", []):
            print(f"--- Searching '{term}' for '{item_name}' ---")

            total_new += run_source("ebay", lambda t: search_ebay(cfg["ebay"], t), item_name, term, conn, ntfy_topic)
            total_new += run_source("reddit", lambda t: search_reddit(cfg["reddit"], t), item_name, term, conn, ntfy_topic)
            total_new += run_source("poshmark", search_poshmark, item_name, term, conn, ntfy_topic)
            total_new += run_source("mercari", search_mercari, item_name, term, conn, ntfy_topic)

            if cfg.get("facebook", {}).get("enabled"):
                total_new += run_source("facebook", search_facebook, item_name, term, conn, ntfy_topic)

    conn.close()
    print(f"\nDone. {total_new} new match(es) found this run.")


if __name__ == "__main__":
    sys.exit(main() or 0)
