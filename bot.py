import os
import json
import requests
from bs4 import BeautifulSoup
import tweepy
from datetime import datetime

# Load credentials
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

# Tweepy client (Only posting works on Free tier)
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Scrape URLs (official)
SOURCE_ACCOUNTS = {
    "infoBMKG": "https://x.com/infoBMKG",
    "BMKG_ACEH": "https://x.com/BMKG_ACEH",
    "BMKG_Official": "https://x.com/BMKG_Official",
    "BNPB_Indonesia": "https://x.com/BNPB_Indonesia",
    "BPBAceh": "https://x.com/BPBAceh",
}

# Aceh-related keywords
ACEH_KEYWORDS = [
    "Aceh", "Banda Aceh", "Aceh Besar", "Sabang", "Pidie", "Pidie Jaya", "Bireuen",
    "Lhokseumawe", "Aceh Utara", "Aceh Timur", "Aceh Tamiang", "Langsa",
    "Aceh Tengah", "Bener Meriah", "Aceh Barat", "Nagan Raya", "Aceh Jaya",
    "Meulaboh", "Aceh Selatan", "Tapaktuan", "Aceh Singkil", "Subulussalam"
]

# Hashtags appended to posts
HASHTAGS = "#CuacaAceh #PeringatanDini #BMKG #Aceh"

# Local cache for last tweet IDs
CACHE_FILE = "cache/last_ids.json"

# Load cache
def load_cache():
    if not os.path.exists("cache"):
        os.makedirs("cache")

    if not os.path.isfile(CACHE_FILE):
        return {}

    with open(CACHE_FILE, "r") as f:
        return json.load(f)

# Save cache
def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)

last_ids = load_cache()

# Scrape tweets from X public webpage
def scrape_tweets(username, url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(f"Error scraping {username}: HTTP {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, "lxml")
    tweets = []

    for div in soup.find_all("div", attrs={"data-testid": "tweet"}):
        text_block = div.find("div", {"data-testid": "tweetText"})
        if not text_block:
            continue

        text = text_block.get_text(strip=True)
        tweet_id = div.get("data-tweet-id")

        # detect image URL (if exists)
        image_tag = div.find("img", {"alt": "Image"})
        image_url = image_tag["src"] if image_tag else None

        tweets.append({
            "id": tweet_id,
            "text": text,
            "image": image_url
        })

    return tweets


# Check for new filtered tweets
def process_account(username, url):
    print(f"Checking {username}...")

    last_seen = last_ids.get(username, None)
    tweets = scrape_tweets(username, url)

    if not tweets:
        return

    new_tweets = []
    for t in tweets:
        if t["id"] == last_seen:
            break
        new_tweets.append(t)

    if new_tweets:
        new_tweets.reverse()

        for t in new_tweets:
            if any(k.lower() in t["text"].lower() for k in ACEH_KEYWORDS):

                final_text = f"{t['text']}\n\n{HASHTAGS}"

                if t["image"]:  
                    filename = "temp.jpg"
                    img = requests.get(t["image"])
                    with open(filename, "wb") as f:
                        f.write(img.content)
                    
                    api.update_status_with_media(status=final_text, filename=filename)
                    print(f"[POSTED WITH IMAGE] {username}")
                else:
                    api.update_status(status=final_text)
                    print(f"[POSTED] {username}")

        # update last seen
        last_ids[username] = tweets[0]["id"]
        save_cache(last_ids)


# MAIN RUN
def main():
    print("=== Aceh Weather Bot Running ===")
    print(datetime.now())

    for username, url in SOURCE_ACCOUNTS.items():
        process_account(username, url)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
