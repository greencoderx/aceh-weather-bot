import os
import tweepy
import requests
import sqlite3
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler

# -----------------------------
# SETUP LOGGING
# -----------------------------
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------
# TELEGRAM CONFIG
# -----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.warning("Telegram not configured.")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        logging.error(f"Telegram error: {e}")

# -----------------------------
# TWITTER API CONFIG
# -----------------------------
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# -----------------------------
# SQLITE SETUP
# -----------------------------
DB_NAME = "tweets.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posted (
            tweet_id TEXT PRIMARY KEY,
            content TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def is_duplicate(tweet_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT tweet_id FROM posted WHERE tweet_id=?", (tweet_id,))
    row = c.fetchone()
    conn.close()
    return row is not None

def save_posted(tweet_id, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO posted (tweet_id, content, created_at) VALUES (?, ?, ?)",
              (tweet_id, content, datetime.utcnow()))
    conn.commit()
    conn.close()

# -----------------------------
# KEYWORD OPTIMIZER
# -----------------------------
KEYWORDS = {
    "gempa": 3,
    "gempabumi": 3,
    "tsunami": 5,
    "peringatan": 2,
    "peringatan dini": 3,
    "waspada": 2,
    "siaga": 2,
    "BMKG": 1,
    "Aceh": 2
}

THRESHOLD_SCORE = 3

def keyword_score(text):
    score = 0
    text_low = text.lower()
    for word, weight in KEYWORDS.items():
        if word in text_low:
            score += weight
    return score

# -----------------------------
# GET BMKG DATA
# -----------------------------
def get_bmkg_data():
    try:
        url = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.xml"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logging.warning("BMKG returned non-200 response")
            return None
        return response.text
    except Exception as e:
        logging.error(f"BMKG fetch error: {e}")
        return None

# -----------------------------
# FORMAT SUMMARY FOR TWITTER
# -----------------------------
def summarize(text):
    if len(text) <= 260:
        return text

    return text[:257] + "..."

# -----------------------------
# MAIN WEATHER BOT LOGIC
# -----------------------------
def process_weather_alerts():
    logging.info("Checking BMKG data...")

    data = get_bmkg_data()
    if not data:
        logging.warning("No data received from BMKG")
        send_telegram_message("⚠️ BMKG data unavailable.")
        return

    # (You can switch to JSON endpoint if needed)
    if "<gempa>" not in data:
        logging.info("No earthquake detected.")
        return

    # Very simple extraction
    try:
        # Extract only raw text content for matching
        text = data.replace("\n", " ")

        score = keyword_score(text)
        if score < THRESHOLD_SCORE:
            logging.info("Tweet ignored due to low keyword score.")
            return

        tweet_id = str(hash(text))

        if is_duplicate(tweet_id):
            logging.info("Duplicate detected. Skipped.")
            return

        summary = summarize(f"BMKG EARTHQUAKE ALERT:\n{text}")

        logging.info("Posting summary to Twitter...")
        api.update_status(summary)

        save_posted(tweet_id, summary)
        send_telegram_message("🚨 Earthquake alert posted to Twitter!")

    except Exception as e:
        logging.error(f"Processing error: {e}")
        send_telegram_message(f"❌ Bot error: {e}")

# -----------------------------
# SCHEDULER (RUN EVERY 5 MIN)
# -----------------------------
def main():
    logging.info("Initializing bot...")
    init_db()

    scheduler = BlockingScheduler()
    scheduler.add_job(process_weather_alerts, "interval", minutes=5)

    logging.info("Bot started. Waiting for triggers...")
    scheduler.start()


if __name__ == "__main__":
    main()
