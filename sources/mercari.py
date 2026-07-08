"""
Mercari has no official public API for third-party search use, so this
uses a headless browser to load search results and read listing cards
from the DOM. Same caveats as poshmark.py: markup can change without
notice, so if this stops returning results, the CSS selectors below are
the first thing to check (open the search URL in a real browser, inspect
a listing card, and update the selectors).
"""
from playwright.sync_api import sync_playwright


def search_mercari(search_term: str, limit: int = 20):
    """
    Returns a list of dicts: {listing_id, title, url, price}
    """
    results = []
    url = f"https://www.mercari.com/search/?keyword={search_term.replace(' ', '%20')}"

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
            page.wait_for_selector("[data-testid='ItemContainer']", timeout=10000)

            cards = page.query_selector_all("[data-testid='ItemContainer']")
            for card in cards[:limit]:
                link_el = card.query_selector("a")
                price_el = card.query_selector("[data-testid='ItemPrice']")

                href = link_el.get_attribute("href") if link_el else None
                if not href:
                    continue

                listing_id = href.rstrip("/").split("/")[-1]
                full_url = href if href.startswith("http") else f"https://www.mercari.com{href}"

                title = link_el.get_attribute("aria-label") or search_term

                results.append(
                    {
                        "listing_id": listing_id,
                        "title": title,
                        "url": full_url,
                        "price": price_el.inner_text().strip() if price_el else None,
                    }
                )
        except Exception as e:
            print(f"[mercari] search failed for '{search_term}': {e}")
        finally:
            browser.close()

    return results
