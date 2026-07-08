"""
Push a notification via ntfy.sh. No account/auth required - it's just a
public pub/sub topic, so pick a topic name that's hard to guess (config.yaml).
"""
import requests


def send_ntfy(topic: str, title: str, message: str, url: str = None):
    headers = {
        "Title": title,
        "Priority": "high",
        "Tags": "teddy_bear",
    }
    if url:
        headers["Click"] = url

    try:
        resp = requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[notify] Failed to send ntfy notification: {e}")
