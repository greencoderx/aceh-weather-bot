import tweepy
import os
from datetime import datetime

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

# File to store daily tweets
DAILY_FILE = "daily_tweets.txt"
LOG_FILE = "bot.log"

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
    for username in usernames:
        try:
            user = client.get_user(username=username)
            if user.data:
                user_ids.append(user.data.id)
                log(f"Fetched ID for {username}: {user.data.id}")
            else:
                log(f"Could not fetch ID for {username}")
        except Exception as e:
            log(f"Error fetching {username}: {e}")
    return user_ids

def main():
    log("Bot started.")
    SOURCE_IDS = get_user_ids(SOURCE_USERNAMES)
    
    for user_id in SOURCE_IDS:
        try:
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
                        except Exception as e:
                            log(f"Error retweeting tweet {tweet.id}: {e}")
                    else:
                        log(f"Skipped tweet {tweet.id} (not Aceh related)")
            else:
                log(f"No tweets found for user {user_id}")
        except Exception as e:
            log(f"Error fetching tweets from user {user_id}: {e}")
    log("Bot finished.\n")

if __name__ == "__main__":
    main()