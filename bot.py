import tweepy
import os
from datetime import datetime
import json

# X API v2 credentials from GitHub secrets
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

# Trusted source usernames
SOURCE_USERNAMES = [
    "infoBMKG",
    "BMKG_ACEH",
    "BMKG_Official",
    "BNPB_Indonesia",
    "BPBD_Aceh"
]

# Aceh keywords (all Kabupaten/Kota)
KEYWORDS = [
    "Aceh Barat", "Aceh Barat Daya", "Aceh Besar", "Aceh Jaya", "Aceh Selatan",
    "Aceh Singkil", "Aceh Tamiang", "Aceh Tengah", "Aceh Tenggara", "Aceh Timur",
    "Aceh Utara", "Bener Meriah", "Bireuen", "Gayo Lues", "Nagan Raya",
    "Pidie", "Pidie Jaya", "Simeulue", "Subulussalam", "Banda Aceh", "Lhokseumawe",
    "Langsa", "Sabang", "Meulaboh"
]

# Hashtags for visibility
HASHTAGS = ["#AcehWeather", "#BMKG", "#CuacaAceh", "#InfoCuaca", "#AcehSiaga"]

# File paths
DAILY_FILE = "daily_tweets.txt"
LOG_FILE = "bot.log"
IDS_FILE = "source_ids.json" # File for caching IDs

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def is_aceh_related(text):
    return any(k.lower() in text.lower() for k in KEYWORDS)

def save_for_digest(tweet_text):
    with open(DAILY_FILE, "a", encoding="utf-8") as f:
        f.write(tweet_text + "\n---\n")

def append_hashtags(text):
    return text + " " + " ".join(HASHTAGS)

def get_user_ids(usernames):
    user_ids = []
    
    # 1. Try to load IDs from a file (Cache Hit)
    if os.path.exists(IDS_FILE):
        try:
            with open(IDS_FILE, "r") as f:
                cached_ids = json.load(f)
                if isinstance(cached_ids, list) and len(cached_ids) == len(usernames):
                    log("Successfully loaded source IDs from cache file.")
                    return cached_ids
                else:
                    log("Cached IDs file was invalid/incomplete. Will fetch from API.")
        except Exception as e:
            log(f"Error reading/parsing {IDS_FILE}: {e}. Proceeding with API lookup.")

    # 2. Fetch IDs from API (Cache Miss)
    log("Fetching user IDs via X API (this only happens if cache is empty/invalid).")
    for username in usernames:
        try:
            user = client.get_user(username=username)
            if user.data:
                user_ids.append(str(user.data.id)) 
                log(f"Fetched ID for {username}: {user.data.id}")
            else:
                log(f"Could not fetch ID for {username}")
        except Exception as e:
            log(f"Error fetching {username}: {e}")

    # 3. Cache the newly fetched IDs to the file
    if len(user_ids) == len(usernames): 
        try:
            with open(IDS_FILE, "w") as f:
                json.dump(user_ids, f)
            log(f"Successfully cached {len(user_ids)} IDs to {IDS_FILE}.")
        except Exception as e:
            log(f"Error writing to {IDS_FILE}: {e}")

    return user_ids

def main():
    log("Bot started.")
    SOURCE_IDS = get_user_ids(SOURCE_USERNAMES)
    
    if not SOURCE_IDS:
        log("No source IDs available. Exiting bot.")
        return

    for user_id in SOURCE_IDS:
        try:
            # This is the rate-limited call. We fetch the latest 5 tweets.
            tweets = client.get_users_tweets(
                id=user_id,
                max_results=5,
                tweet_fields=["id","text","created_at"]
            )

            if tweets.data:
                for tweet in tweets.data:
                    if is_aceh_related(tweet.text):
                        try:
                            client.retweet(tweet.id)
                            save_for_digest(tweet.text)
                            log(f"Retweeted tweet {tweet.id} from user {user_id}")
                        except tweepy.errors.Forbidden as e:
                            # Handle the case where the tweet was already retweeted.
                            if "You have already retweeted this Tweet" in str(e):
                                log(f"Tweet {tweet.id} from user {user_id} was already retweeted. Skipping.")
                            else:
                                log(f"Error retweeting tweet {tweet.id}: {e}")
                        except Exception as e:
                            log(f"General error retweeting tweet {tweet.id}: {e}")
                    else:
                        log(f"Skipped tweet {tweet.id} (not Aceh related)")
            else:
                log(f"No tweets found for user {user_id}")
        except Exception as e:
            log(f"Error fetching tweets from user {user_id}: {e}")
            
    log("Bot finished.\n")

if __name__ == "__main__":
    main()
