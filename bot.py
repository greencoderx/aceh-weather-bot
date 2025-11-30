import os
import tweepy
import time
from datetime import datetime, timedelta

# Authenticate using OAuth 1.0a (READ + WRITE)
auth = tweepy.OAuth1UserHandler(
    os.getenv("API_KEY"),
    os.getenv("API_SECRET"),
    os.getenv("ACCESS_TOKEN"),
    os.getenv("ACCESS_SECRET")
)

api = tweepy.API(auth)

# ------------------------------
# SOURCE ACCOUNTS
# ------------------------------
SOURCE_ACCOUNTS = [
    "infoBMKG",
    "BMKG_ACEH",
    "BMKG_Official",
    "BNPB_Indonesia",
    "BPBD_Aceh"
]

# ------------------------------
# KEYWORDS FOR ALL ACEH REGIONS
# ------------------------------
ACEH_KEYWORDS = [
    "aceh", "banda aceh", "sabang", "lhokseumawe", "langsa", "subulussalam",
    "aceh besar", "pidie", "pidie jaya", "aceh utara", "aceh timur",
    "aceh tamiang", "aceh tengah", "aceh tenggara", "aceh selatan",
    "aceh singkil", "aceh jaya", "aceh barat", "aceh barat daya",
    "gayo lues", "bener meriah", "nagan raya", "simeulue"
]

# ------------------------------
# HASHTAGS FOR VISIBILITY
# ------------------------------
HASHTAGS = [
    "#Aceh", "#InfoAceh", "#BMKG", "#CuacaAceh", "#PeringatanDini",
    "#BencanaAceh", "#Gempa", "#HujanLebat", "#PeringatanCuaca"
]

# ------------------------------
# MEMORY FILE FOR LAST TWEET
# ------------------------------
LAST_ID_FILE = "last_seen_id.txt"

def load_last_seen():
    if not os.path.exists(LAST_ID_FILE):
        return 0
    with open(LAST_ID_FILE, "r") as f:
        return int(f.read().strip())

def save_last_seen(tweet_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(tweet_id))

# ------------------------------
# FETCH + POST LOGIC
# ------------------------------
def fetch_and_post():
    last_seen_id = load_last_seen()

    for account in SOURCE_ACCOUNTS:
        try:
            print(f"Checking tweets from {account}...")
            tweets = api.user_timeline(
                screen_name=account,
                since_id=last_seen_id,
                tweet_mode="extended",
                count=10
            )

            for tweet in reversed(tweets):
                text_lower = tweet.full_text.lower()

                if any(keyword in text_lower for keyword in ACEH_KEYWORDS):
                    print(f"Matched tweet from {account}: {tweet.id}")

                    hashtags_text = " ".join(HASHTAGS)
                    final_text = f"{tweet.full_text}\n\nSource: @{account}\n{hashtags_text}"

                    api.update_status(final_text)
                    save_last_seen(tweet.id)

        except Exception as e:
            print(f"Error fetching tweets from {account}: {e}")

# ------------------------------
# MAIN LOOP
# ------------------------------
if __name__ == "__main__":
    print("🚀 Aceh Weather Bot started...")
    while True:
        fetch_and_post()
        time.sleep(30)
