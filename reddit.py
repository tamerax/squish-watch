"""
Reddit search across configured subreddits using PRAW, authenticated via
your approved Reddit developer app credentials.

Setup: developers.reddit.com -> your approved app -> client_id is the
string under the app name, client_secret is labeled "secret". Put both
in config.yaml under reddit:.

This uses PRAW's read-only application mode (client_id + client_secret +
user_agent, no username/password) which is sufficient for searching
public subreddit content.
"""
import praw


def _get_reddit(cfg: dict):
    return praw.Reddit(
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
        user_agent=cfg.get("user_agent", "squish-watch script"),
    )


def search_reddit(cfg: dict, search_term: str, limit: int = 15):
    """
    Returns a list of dicts: {listing_id, title, url, price}
    Searches new posts across configured subreddits for the search term.
    price is always None since Reddit posts don't have structured pricing.
    """
    reddit = _get_reddit(cfg)
    subreddit_str = "+".join(cfg.get("subreddits", ["Squishable"]))
    subreddit = reddit.subreddit(subreddit_str)

    results = []
    for submission in subreddit.search(search_term, sort="new", time_filter="month", limit=limit):
        results.append(
            {
                "listing_id": submission.id,
                "title": submission.title,
                "url": f"https://reddit.com{submission.permalink}",
                "price": None,
            }
        )
    return results
