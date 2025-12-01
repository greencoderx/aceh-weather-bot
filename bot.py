import tweepy
import os
from datetime import datetime

print("=== Aceh Weather Bot Running ===")
print(datetime.now())

# -------------------------------------------------------
# TWITTER CREDENTIALS
# -------------------------------------------------------
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    wait_on_rate_limit=True
)

# -------------------------------------------------------
# SOURCE ACCOUNTS TO MONITOR
# -------------------------------------------------------
SOURCE_ACCOUNTS = {
    "infoBMKG": "250405606",         # BMKG
    "BMKG_ACEH": "1316488859874965504",
    "BMKG_Official": "253855545",    
    "BNPB_Indonesia": "114547606",
    "BPBAceh": "2724442720"
}

# -------------------------------------------------------
# ACEH KEYWORDS (FULL LIST OF KABUPATEN + GEMPA TERMS)
# -------------------------------------------------------
ACEH_KEYWORDS = [
    # Provinces / General
    "ACEH", "NAD", "SERAMBI",

    # Major cities
    "BANDA ACEH", "LANGSA", "LHOKSEUMAWE", "SUBULUSSALAM", "SABANG",

    # All districts (Kabupaten Aceh)
    "ACEH BESAR", "PIDIE", "PIDIE JAYA", "BIREUEN", "BENER MERIAH",
    "ACEH UTARA", "ACEH TIMUR", "ACEH TENGAH", "ACEH BARAT",
    "ACEH BARAT DAYA", "ACEH SELATAN", "ACEH SINGKIL",
    "ACEH TAMIANG", "ACEH TENGGARA", "ACEH JAYA", "GAYO LUES",
    "NAGAN RAYA", "SIMEULUE",

    # Specific locations BMKG often posts
    "TAKENGON", "MEULABOH", "CALANG", "TAPAKTUAN",
    "BLANGKEJEREN", "LHOKSEUMAWE", "IDI", "SIGLI", "LOTENG",

    # Gempa terms
    "GEMPA", "MAG", "M=.", "KEPUATAN", "TEKTONIK",
    "PUSAT GEMPA", "KM", "BMKG"
]

# Convert keywords to lowercase for matching
ACEH_KEYWORDS = [k.lower() for k in ACEH_KEYWORDS]

# -------------------------------------------------------
# LOAD LAST RETWEETED TWEETS
# -------------------------------------------------------
LAST_FILE = "last_tweets.txt"
if not os.path.exists(LAST_FILE):
    open(LAST_FILE, "w").close()

with open(LAST_FILE, "r") as f:
    processed_ids = set(line.strip() for line in f if line.strip())

# -------------------------------------------------------
# CHECK EACH SOURCE ACCOUNT
# -------------------------------------------------------
def keyword_match(text):
    text = text.lower()
    return any(k in text for k in ACEH_KEYWORDS)

def save_processed(tweet_id):
    with open(LAST_FILE, "a") as f:
        f.write(str(tweet_id) + "\n")

for username, user_id in SOURCE_ACCOUNTS.items():
    try:
        print(f"Checking {username}...")

        tweets = client.get_users_tweets(
            id=user_id,
            max_results=5,
            tweet_fields=["id", "text", "created_at"]
        )

        if not tweets.data:
            continue

        for t in tweets.data:
            tid = str(t.id)
            text = t.text

            # Avoid duplicate processing
            if tid in processed_ids:
                continue

            # Keyword check
            if not keyword_match(text):
                continue

            print(f"MATCH FOUND from @{username}:")
            print(text)
            print("Retweeting...")

            try:
                client.retweet(tid)
                print("Retweeted successfully!")
            except Exception as e:
                print("Retweet error:", e)

            processed_ids.add(tid)
            save_processed(tid)

    except Exception as e:
        print(f"Error checking {username}: {e}")

print("=== DONE ===")
