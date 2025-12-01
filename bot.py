import os
import tweepy
import requests
from datetime import datetime

print("=== Aceh Weather Bot Running ===")
print(datetime.now())

# Load environment variables
API_KEY = os.environ.get("TWITTER_API_KEY")
API_SECRET = os.environ.get("TWITTER_API_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

# Authenticate (OAuth 1.0a for retweet)
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Source accounts to monitor
SOURCE_ACCOUNTS = [
    "infoBMKG",
    "BMKG_ACEH",
    "BMKG_Official",
    "BNPB_Indonesia",
    "BPBAceh"
]

# Aceh-related keywords
KEYWORDS = [
    "aceh", "banda aceh", "pidie", "pidie jaya", "bireuen", "lhokseumawe", "langsa",
    "aceh utara", "aceh besar", "aceh barat", "aceh selatan", "aceh tenggara",
    "simeulue", "sabussalam", "bener meriah", "aceh tengah", "gayo", "singkil"
]

# Hashtags to append
HASHTAGS = "#Aceh #BMKG #InfoGempa"

# File to store last seen tweet IDs
LAST_TWEET_FILE = "last_tweets.txt"

# Initialize storage
if not os.path.exists(LAST_TWEET_FILE):
    with open(LAST_TWEET_FILE, "w") as f:
        f.write("")

def load_last_seen():
    if not os.path.exists(LAST_TWEET_FILE):
        return {}
    with open(LAST_TWEET_FILE) as f:
        lines = f.read().splitlines()
        data = {}
        for line in lines:
            if ":" in line:
                user, tweet_id = line.split(":")
                data[user] = int(tweet_id)
        return data

def save_last_seen(data):
    with open(LAST_TWEET_FILE, "w") as f:
        for user, tweet_id in data.items():
            f.write(f"{user}:{tweet_id}\n")

last_seen = load_last_seen()

# === PROCESS EACH SOURCE ACCOUNT ===
for username in SOURCE_ACCOUNTS:
    print(f"Checking {username}...")

    try:
        # Fetch latest tweets
        tweets = api.user_timeline(
            screen_name=username,
            count=5,
            tweet_mode="extended"
        )
    except Exception as e:
        print(f"Error checking {username}: {e}")
        continue

    for tweet in tweets:
        text = tweet.full_text.lower()

        # Skip if already retweeted
        if username in last_seen and tweet.id <= last_seen[username]:
            continue

        # Filter relevant tweets
        if not any(keyword in text for keyword in KEYWORDS):
            continue

        # Retweet
        try:
            api.retweet(tweet.id)
            print(f"Retweeted: {tweet.id}")

            # Optional: Post a quote tweet with extra hashtags
            api.update_status(
                status=f"{HASHTAGS}",
                attachment_url=f"https://twitter.com/{username}/status/{tweet.id}"
            )

        except Exception as e:
            print(f"Retweet failed: {e}")

        # Update last seen
        last_seen[username] = tweet.id

# Save last seen
save_last_seen(last_seen)

print("=== DONE ===")
