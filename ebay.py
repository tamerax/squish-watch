"""
eBay Browse API search.

Uses the client-credentials OAuth flow (app-only token) which is all you
need for public item searches - no user login required.

Setup: developer.ebay.com -> register -> create a "Production" keyset ->
copy Client ID / Client Secret into config.yaml.
"""
import time
import requests

_TOKEN_CACHE = {"token": None, "expires_at": 0}


def _get_app_token(client_id: str, client_secret: str) -> str:
    now = time.time()
    if _TOKEN_CACHE["token"] and now < _TOKEN_CACHE["expires_at"] - 60:
        return _TOKEN_CACHE["token"]

    resp = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    _TOKEN_CACHE["token"] = data["access_token"]
    _TOKEN_CACHE["expires_at"] = now + data.get("expires_in", 7200)
    return _TOKEN_CACHE["token"]


def search_ebay(cfg: dict, search_term: str, limit: int = 20):
    """
    Returns a list of dicts: {listing_id, title, url, price}
    """
    token = _get_app_token(cfg["client_id"], cfg["client_secret"])

    resp = requests.get(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        headers={
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": cfg.get("marketplace", "EBAY_US"),
        },
        params={
            "q": search_term,
            "limit": limit,
            "sort": "newlyListed",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("itemSummaries", []):
        results.append(
            {
                "listing_id": item.get("itemId"),
                "title": item.get("title"),
                "url": item.get("itemWebUrl"),
                "price": (item.get("price") or {}).get("value"),
            }
        )
    return results
