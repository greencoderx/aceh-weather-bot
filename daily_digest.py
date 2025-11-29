import tweepy
import os
from datetime import datetime

# X API v2 credentials
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    wait_on_rate_limit=True
)

DAILY_FILE = "daily_tweets.txt"
HASHTAGS = ["#AcehWeather", "#BMKG", "#CuacaAceh", "#InfoCuaca", "#AcehSiaga"]
LOG_FILE = "bot.log"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def append_hashtags(text):
    return text + " " + " ".join(HASHTAGS)

def post_daily_digest():
    log("Starting daily digest.")
    try:
        with open(DAILY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if content:
            chunk_size = 270 - len(" ".join(HASHTAGS)) - 1
            lines = content.split("\n---\n")
            tweet_chunks = []
            current_chunk = ""
            for line in lines:
                if len(current_chunk) + len(line) + 3 <= chunk_size:
                    current_chunk += line + "\n---\n"
                else:
                    tweet_chunks.append(current_chunk.strip())
                    current_chunk = line + "\n---\n"
            if current_chunk:
                tweet_chunks.append(current_chunk.strip())

            for chunk in tweet_chunks:
                try:
                    client.create_tweet(text=append_hashtags(chunk))
                    log("Posted digest tweet successfully.")
                except Exception as e:
                    log(f"Error posting digest tweet: {e}")
            
            open(DAILY_FILE, "w").close()
            log("Daily digest completed and file cleared.")
        else:
            log("No tweets to post today for daily digest.")

    except FileNotFoundError:
        log("Daily file not found, nothing to post.")

if __name__ == "__main__":
    post_daily_digest()