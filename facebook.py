"""
PLACEHOLDER - not implemented yet.

Facebook Marketplace/Groups have no public API for this use case. A working
version would need:
  1. A persisted logged-in session (Playwright storage_state json), since
     Facebook blocks anonymous automated access almost immediately.
  2. Specific group URLs to poll (set facebook.groups in config.yaml).
  3. Periodic manual re-login when the session gets invalidated (FB does
     this proactively to logged-in-looking bots) - budget for this being
     the most maintenance-heavy part of the whole system.

When you're ready to wire this up, the shape should mirror poshmark.py /
mercari.py: a search_facebook(search_term, limit) function returning
[{listing_id, title, url, price}, ...], called from main.py the same way.
"""


def search_facebook(search_term: str, limit: int = 20):
    # Intentionally returns nothing until configured.
    return []
