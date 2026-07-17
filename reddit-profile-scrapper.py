import csv
import sys
import warnings
from pathlib import Path

import requests
import urllib3
from tqdm import tqdm

# Suppress urllib3 InsecureRequestWarning and other warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

POSTS_URL = "https://arctic-shift.photon-reddit.com/api/posts/search"
COMMENTS_URL = "https://arctic-shift.photon-reddit.com/api/comments/search"
OUTPUT_DIR = Path("data/profiles")
FIELDNAMES = ["text", "created_utc", "subreddit", "id", "author", "is_comment"]


def fetch(url, username):
    try:
        response = requests.get(url, params={"author": username, "limit": "auto"}, verify=False, timeout=30)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"Failed to fetch {url} for {username}. Error: {e}")
        return []


def post_text(item):
    title = (item.get("title") or "").strip()
    selftext = (item.get("selftext") or "").strip()
    if selftext and selftext not in ("[deleted]", "[removed]"):
        return f"{title}\n\n{selftext}".strip()
    return title


def comment_text(item):
    return (item.get("body") or "").strip()


def fetch_user_history(username):
    rows = []
    for item in fetch(POSTS_URL, username):
        rows.append({
            "text": post_text(item),
            "created_utc": item.get("created_utc"),
            "subreddit": item.get("subreddit"),
            "id": item.get("id"),
            "author": item.get("author"),
            "is_comment": False,
        })
    for item in fetch(COMMENTS_URL, username):
        rows.append({
            "text": comment_text(item),
            "created_utc": item.get("created_utc"),
            "subreddit": item.get("subreddit"),
            "id": item.get("id"),
            "author": item.get("author"),
            "is_comment": True,
        })
    rows.sort(key=lambda r: r["created_utc"] or 0)
    return rows


def strip_username_prefix(name):
    for prefix in ("/u/", "u/"):
        if name.startswith(prefix):
            return name[len(prefix):]
    return name


def read_usernames(input_path):
    usernames = []
    for line in Path(input_path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        usernames.append(strip_username_prefix(line))
    return usernames


def main():
    if len(sys.argv) != 2:
        print("Usage: python reddit-profile-scrapper.py <usernames.txt>")
        sys.exit(1)

    usernames = read_usernames(sys.argv[1])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for username in tqdm(usernames, desc="Fetching user histories"):
        rows = fetch_user_history(username)
        out_path = OUTPUT_DIR / f"{username}.csv"
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    main()
