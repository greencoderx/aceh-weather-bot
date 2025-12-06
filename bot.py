import os
import tweepy
from datetime import datetime

print("=== Aceh Weather Bot Running ===")
print(datetime.now())

# Load credentials
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Authenticate
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Source accounts
ACCOUNTS = [
    "infoBMKG",
    "BMKG_ACEH",
    "BMKG_Official",
    "BNPB_Indonesia",
    "BPBAceh"
]

# Aceh-related keywords
KEYWORDS = [
    "aceh", "banda aceh", "pidie", "pidie jaya",
    "bireuen", "lhokseumawe", "langsa", "aceh utara",
    "aceh besar", "simeulue", "meulaboh", "aceh barat"
]

# Track last tweets
TRACK_FILE = "last_tweets.txt"

if not os.path.exists(TRACK_FILE):
    with open(TRACK_FILE, "w") as f:
        f.write("")

def load_last():
    data = {}
    with open(TRACK_FILE, "r") as f:
        for line in f:
            if ":" in line:
                user, tid = line.strip().split(":")
                data[user] = int(tid)
    return data

def save_last(data):
    with open(TRACK_FILE, "w") as f:
        for user, tid in data.items():
            f.write(f"{user}:{tid}\n")

last_seen = load_last()

# === MAIN LOOP ===
for user in ACCOUNTS:
    print(f"Checking {user}...")

    try:
        tweets = api.user_timeline(screen_name=user, count=5, tweet_mode="extended")
    except Exception as e:
        print(f"Error checking {user}: {e}")
        continue

    for t in tweets:
        text = t.full_text.lower()

        if user in last_seen and t.id <= last_seen[user]:
            continue

        if not any(k in text for k in KEYWORDS):
            continue

        try:
            api.retweet(t.id)
            print(f"Retweeted {t.id} from {user}")
        except Exception as e:
            print(f"Retweet error: {e}")

        last_seen[user] = t.id

save_last(last_seen)

print("=== DONE ===")
