import tweepy
import os

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

def append_hashtags(text):
    return text + " " + " ".join(HASHTAGS)

def post_daily_digest():
    try:
        with open(DAILY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if content:
            # Split content into 270-char chunks to leave room for hashtags
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
                client.create_tweet(text=append_hashtags(chunk))
            print("Daily digest posted!")
            open(DAILY_FILE, "w").close()
        else:
            print("No tweets to post today.")
    except FileNotFoundError:
        print("No daily file found.")

if __name__ == "__main__":
    post_daily_digest()
