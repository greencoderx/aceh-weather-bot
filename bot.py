import os
import logging
from datetime import datetime
import tweepy
import requests
from bs4 import BeautifulSoup

# ===========================
# Logging Setup
# ===========================
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("=== Aceh Weather Bot Starting ===")

# ===========================
# Twitter API Authentication
# ===========================
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# v1.1 API for media upload
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api_v1 = tweepy.API(auth)

# ===========================
# Helper: Load/Save Last Summary
# ===========================
LAST_FILE = "last_summary.txt"

def load_last_summary():
    if not os.path.exists(LAST_FILE):
        return ""
    with open(LAST_FILE, "r") as f:
        return f.read().strip()

def save_last_summary(text):
    with open(LAST_FILE, "w") as f:
        f.write(text)

# ===========================
# Scrape BMKG Weather Summary
# ===========================
def get_bmkg_summary():
    try:
        url = "https://www.bmkg.go.id/cuaca/prakiraan-cuaca-indonesia.bmkg?Prov=07"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        area = soup.select_one(".prakicu-kota h2")
        weather = soup.select_one(".prakicu-kota img")
        desc = soup.select_one(".prakicu-kota .keterangan")

        if not area:
            return None

        location = area.text.strip()
        detail = desc.text.strip() if desc else "Cuaca tidak tersedia"
        image_url = weather["src"] if weather else None

        summary = f"BMKG Aceh Update:\nLokasi: {location}\nCuaca: {detail}\nSumber: bmkg.go.id"
        return summary, image_url

    except Exception as e:
        logging.error(f"BMKG scrape error: {e}")
        return None

# ===========================
# Download Image (if any)
# ===========================
def download_image(url):
    try:
        r = requests.get(url)
        filename = "weather.png"
        with open(filename, "wb") as f:
            f.write(r.content)
        return filename
    except:
        return None

# ===========================
# Post Tweet with Media
# ===========================
def post_tweet(text, media=None):
    try:
        if media:
            media_id = api_v1.media_upload(media).media_id_string
            client.create_tweet(text=text, media_ids=[media_id])
        else:
            client.create_tweet(text=text)

        logging.info(f"Tweet posted: {text[:50]}...")
        print("Tweet posted")
    except Exception as e:
        logging.error(f"Tweet error: {e}")
        print(f"Tweet error: {e}")

# ===========================
# MAIN
# ===========================
if __name__ == "__main__":

    logging.info("Running weather scrape task...")

    result = get_bmkg_summary()
    if not result:
        print("No data received from BMKG")
        exit()

    summary, img = result

    last = load_last_summary()

    if summary == last:
        print("⏭ No new update. Skipping.")
        logging.info("Duplicate summary. Skipped.")
        exit()

    # Download weather icon if exists
    img_path = download_image(img) if img else None

    # Post tweet
    post_tweet(summary, img_path)

    # Save last posted summary
    save_last_summary(summary)

    print("=== DONE ===")
    logging.info("=== Task Completed ===")
