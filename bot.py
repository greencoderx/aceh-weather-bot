import os
import time
import requests
from bs4 import BeautifulSoup
import tweepy

# ==============================
# X API Credentials
# ==============================
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# ==============================
# Source accounts to scrape
# ==============================
SOURCE_ACCOUNTS = [
    "infoBMKG",
    "BMKG_ACEH",
    "BMKG_Official",
    "BNPB_Indonesia",
    "BPBD_Aceh"
]

# ==============================
# Storage for last tweet
# ==============================
STATE_FILE = "last_tweets.txt"

def load_last_tweets():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        lines = f.readlines()
    data = {}
    for line in lines:
        user, tweet_id = line.strip().split(",")
        data[user] = tweet_id
    return data

def save_last_tweets(data):
    with open(STATE_FILE, "w") as f:
        for user, tweet_id in data.items():
            f.write(f"{user},{tweet_id}\n")

# ==============================
# Scrape a user's latest tweet
# ==============================
def scrape_latest_tweet(username):
    url = f"https://x.com/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # Find tweet text (simple pattern)
    tweet_containers = soup.find_all("div", attrs={"data-testid": "tweet"})

    if not tweet_containers:
        print(f"❌ Could not find any tweets for {username}")
        return None, None

    first_tweet = tweet_containers[0]

    tweet_text_div = first_tweet.find("div", {"lang": True})
    tweet_text = tweet_text_div.get_text(strip=True) if tweet_text_div else ""

    tweet_id = first_tweet.get("data-tweet-id")
    if not tweet_id:
        tweet_id = str(int(time.time()))  # fallback

    return tweet_id, tweet_text


# ==============================
# Main bot logic
# ==============================
def run_bot():
    print("🚀 Aceh Weather Bot (Scraper Version) Started")

    last_tweets = load_last_tweets()

    for account in SOURCE_ACCOUNTS:
        print(f"\n🔍 Checking {account} ...")

        try:
            tweet_id, text = scrape_latest_tweet(account)
        except Exception as e:
            print(f"❌ Error scraping {account}: {e}")
            continue

        if not tweet_id or not text:
            print(f"⚠ No tweet found for {account}")
            continue

        # Check if new tweet
        if account in last_tweets and last_tweets[account] == tweet_id:
            print(f"⏭ No new tweet from {account}")
            continue

        # New tweet found → Repost
        try:
            print(f"🔁 Reposting from {account}: {text[:50]}...")
            api.update_status(f"Repost from @{account}:\n\n{text}")
            last_tweets[account] = tweet_id
        except Exception as e:
            print(f"❌ Error reposting: {e}")

    save_last_tweets(last_tweets)
    print("\n✅ Bot finished!")


if __name__ == "__main__":
    run_bot()
