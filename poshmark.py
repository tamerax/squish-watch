"""
Poshmark has no public search API, so this uses a headless browser to load
their search results page and read the listing cards out of the DOM.

Poshmark's ToS restricts automated scraping - this polls infrequently
(once per your cron interval) and only reads public search results, but
be aware this could break at any time if they change their markup, and
heavy polling could get your IP rate-limited or blocked. Keep the poll
interval reasonable (20+ minutes).
"""
from playwright.sync_api import sync_playwright


def search_poshmark(search_term: str, limit: int = 20):
    """
    Returns a list of dicts: {listing_id, title, url, price}
    """
    results = []
    url = f"https://poshmark.com/search?query={search_term.replace(' ', '%20')}&type=listings"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        )
        try:
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            page.wait_for_selector("[data-et-name='listing']", timeout=10000)

            cards = page.query_selector_all("[data-et-name='listing']")
            for card in cards[:limit]:
                link_el = card.query_selector("a")
                title_el = card.query_selector("[data-test='title']") or card.query_selector("a")
                price_el = card.query_selector("[data-test='price']")

                href = link_el.get_attribute("href") if link_el else None
                if not href:
                    continue

                listing_id = href.rstrip("/").split("/")[-1]
                full_url = href if href.startswith("http") else f"https://poshmark.com{href}"

                results.append(
                    {
                        "listing_id": listing_id,
                        "title": title_el.inner_text().strip() if title_el else search_term,
                        "url": full_url,
                        "price": price_el.inner_text().strip() if price_el else None,
                    }
                )
        except Exception as e:
            print(f"[poshmark] search failed for '{search_term}': {e}")
        finally:
            browser.close()

    return results
