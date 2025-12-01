import os
import json
import requests
import tweepy
from datetime import datetime

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

SOURCE_ACCOUNTS = [
    "infoBMKG",
    "BMKG_ACEH",
    "BMKG_Official",
    "BNPB_Indonesia",
    "BPBAceh"
]

ACEH_KEYWORDS = [
    "Aceh", "Banda Aceh", "Aceh Besar", "Sabang", "Pidie", "Pidie Jaya", "Bireuen",
    "Lhokseumawe", "Aceh Utara", "Aceh Timur", "Aceh Tamiang", "Langsa",
    "Aceh Tengah", "Bener Meriah", "Aceh Barat", "Nagan Raya", "Aceh Jaya",
    "Meulaboh", "Aceh Selatan", "Tapaktuan", "Aceh Singkil", "Subulussalam"
]

HASHTAGS = "#CuacaAceh #PeringatanDini #BMKG #Aceh"

CACHE_FILE = "cache/last_ids.json"


def load_cache():
    if not os.path.exists("cache"):
        os.makedirs("cache")
    if not os.path.isfile(CACHE_FILE):
        return {}
    return json.load(open(CACHE_FILE, "r"))


def save_cache(data):
    json.dump(data, open(CACHE_FILE, "w"))


last_ids = load_cache()


def fetch_from_syndication(username):
    url = f"https://cdn.syndication.twimg.com/timeline/profile?screen_name={username}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Failed to fetch {username}: {r.status_code}")
        return []

    data = r.json()
    if "tweets" not in data:
        print(f"No tweets found for {username}")
        return []

    tweets = []

    for t in data["tweets"]:
        tweet_id = t.get("id_str")
        text = t.get("text")
        media_url = None

        # check image
        if "mediaDetails" in t and len(t["mediaDetails"]) > 0:
            for m in t["mediaDetails"]:
                if m.get("media_url_https"):
                    media_url = m["media_url_https"]

        tweets.append({
            "id": tweet_id,
            "text": text,
            "image": media_url
        })

    return tweets


def process_account(username):
    print(f"Checking {username}...")
    last_seen = last_ids.get(username)

    tweets = fetch_from_syndication(username)
    if not tweets:
        print(f"No tweets for {username}")
        return

    new_tweets = []
    for t in tweets:
        if t["id"] == last_seen:
            break
        new_tweets.append(t)

    if new_tweets:
        new_tweets.reverse()
        for t in new_tweets:

            # Only post tweet if it contains Aceh-related keywords
            if not any(k.lower() in t["text"].lower() for k in ACEH_KEYWORDS):
                continue

            status = f"{t['text']}\n\n{HASHTAGS}"

            if t["image"]:
                img = requests.get(t["image"])
                with open("temp.jpg", "wb") as f:
                    f.write(img.content)
                api.update_status_with_media(status=status, filename="temp.jpg")
                print(f"[POSTED WITH IMAGE] {username}")
            else:
                api.update_status(status=status)
                print(f"[POSTED] {username}")

        last_ids[username] = tweets[0]["id"]
        save_cache(last_ids)


def main():
    print("=== Aceh Weather Bot Running ===")
    print(datetime.now())
    for acc in SOURCE_ACCOUNTS:
        process_account(acc)
    print("=== DONE ===")


if __name__ == "__main__":
    main()
