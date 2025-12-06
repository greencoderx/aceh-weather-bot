import os
import json
import time
import hashlib
import logging
import requests
import tweepy
from datetime import datetime

# -----------------------------------------------------------
# Logging setup
# -----------------------------------------------------------
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("=== Aceh Weather Bot Running ===")
print(datetime.now())

logging.info("Bot started")

# -----------------------------------------------------------
# Setup Twitter API
# -----------------------------------------------------------
api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_secret = os.getenv("TWITTER_ACCESS_SECRET")

client = tweepy.Client(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_secret
)

# -----------------------------------------------------------
# Load/Save last post hash to avoid duplicates
# -----------------------------------------------------------
HASH_FILE = "last_hash.txt"

def get_last_hash():
    if not os.path.exists(HASH_FILE):
        return None
    return open(HASH_FILE).read().strip()

def save_hash(h):
    with open(HASH_FILE, "w") as f:
        f.write(h)

# -----------------------------------------------------------
# Step 1: Fetch Weather Data from BMKG Public API
# -----------------------------------------------------------
def fetch_weather():
    """
    BMKG provides open data through:
    https://data.bmkg.go.id/
    We'll use one of the public JSON endpoints.
    """
    url = "https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Aceh.json"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error(f"Failed to fetch BMKG data: {e}")
        return None

# -----------------------------------------------------------
# Step 2: Parse summary
# -----------------------------------------------------------
def summarize_weather(data):
    try:
        province = data["data"]["forecast"]["area"][0]
        name = province["name"]
        params = province["parameter"]

        weather = params[6]["timerange"][0]["value"][0]["#text"]
        temp = params[5]["timerange"][0]["value"][0]["#text"]

        summary = (
            f"🌦️ *Prakiraan Cuaca Aceh*\n"
            f"Wilayah: {name}\n"
            f"Cuaca: {weather}\n"
            f"Suhu: {temp}°C\n"
            f"Sumber: BMKG"
        )

        return summary

    except Exception as e:
        logging.error(f"Failed to summarize weather: {e}")
        return None

# -----------------------------------------------------------
# Step 3: Detect duplicate content
# -----------------------------------------------------------
def is_duplicate(text):
    hash_val = hashlib.md5(text.encode()).hexdigest()
    last = get_last_hash()
    if last == hash_val:
        return True
    save_hash(hash_val)
    return False

# -----------------------------------------------------------
# Step 4: Upload media (optional)
# -----------------------------------------------------------
def upload_media(image_path):
    try:
        media = client.media_upload(filename=image_path)
        return media.media_id
    except Exception as e:
        logging.error(f"Media upload failed: {e}")
        return None

# -----------------------------------------------------------
# Step 5: Post tweet
# -----------------------------------------------------------
def post_tweet(text, media_id=None):
    try:
        if media_id:
            client.create_tweet(text=text, media_ids=[media_id])
        else:
            client.create_tweet(text=text)

        logging.info("Tweet posted successfully")
        print("Tweet posted successfully")

    except Exception as e:
        logging.error(f"Tweet failed: {e}")
        print(f"Tweet failed: {e}")

# -----------------------------------------------------------
# MAIN PROCESS
# -----------------------------------------------------------
def main():
    data = fetch_weather()
    if not data:
        print("Failed to fetch weather")
        return

    summary = summarize_weather(data)
    if not summary:
        print("Failed to summarize")
        return

    print(summary)

    if is_duplicate(summary):
        print("Duplicate detected, skipping tweet.")
        logging.info("Duplicate tweet skipped")
        return

    post_tweet(summary)


if __name__ == "__main__":
    main()
    print("=== DONE ===")
