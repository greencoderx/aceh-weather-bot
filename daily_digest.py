import tweepy
import os

# X API keys
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

DAILY_FILE = "daily_tweets.txt"
HASHTAGS = ["#AcehWeather", "#BMKG", "#CuacaAceh", "#InfoCuaca", "#AcehSiaga"]

def append_hashtags(text):
    return text + " " + " ".join(HASHTAGS)

def post_daily_digest():
    try:
        with open(DAILY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if content:
            # Split into chunks if too long for a tweet (max 280 chars)
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

            # Post each chunk as a separate tweet
            for chunk in tweet_chunks:
                api.update_status(append_hashtags(chunk))
            print("Daily digest posted!")

            # Clear file for next day
            open(DAILY_FILE, "w").close()
        else:
            print("No tweets to post today.")

    except FileNotFoundError:
        print("No daily file found.")

if __name__ == "__main__":
    post_daily_digest()