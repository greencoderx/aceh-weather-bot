import tweepy
import os
import json

# Credentials
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

# Source accounts
SOURCE_USERNAMES = [
    "infoBMKG", "BMKG_ACEH", "BMKG_Official",
    "BNPB_Indonesia", "BPBD_Aceh"
]

# Load last seen tweet IDs
LAST_SEEN_FILE = "last_seen.json"
if os.path.exists(LAST_SEEN_FILE):
    with open(LAST_SEEN_FILE, "r") as f:
        last_seen = json.load(f)
else:
    last_seen = {}

# Keywords
KEYWORDS = [
    "Aceh Barat", "Aceh Barat Daya", "Aceh Besar", "Aceh Jaya", "Aceh Selatan",
    "Aceh Singkil", "Aceh Tamiang", "Aceh Tengah", "Aceh Tenggara", "Aceh Timur",
    "Aceh Utara", "Bener Meriah", "Bireuen", "Gayo Lues", "Nagan Raya",
    "Pidie", "Pidie Jaya", "Simeulue", "Subulussalam", "Banda Aceh", "Lhokseumawe",
    "Langsa", "Sabang", "Meulaboh"
]

HASHTAGS = ["#AcehWeather", "#BMKG", "#CuacaAceh", "#InfoCuaca", "#AcehSiaga"]

DAILY_FILE = "daily_tweets.txt"


def save_for_digest(text):
    with open(DAILY_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n---\n")


def append_hashtags(text):
    return text + " " + " ".join(HASHTAGS)


def is_aceh_related(text):
    return any(k.lower() in text.lower() for k in KEYWORDS)


def get_user_ids():
    ids = {}
    for username in SOURCE_USERNAMES:
        try:
            user = client.get_user(username=username)
            if user.data:
                ids[username] = user.data.id
        except Exception as e:
            print(f"Error fetching {username}: {e}")
    return ids


def main():
    global last_seen

    user_ids = get_user_ids()

    for username, uid in user_ids.items():
        try:
            since_id = last_seen.get(username)

            tweets = client.get_users_tweets(
                id=uid,
                since_id=since_id,
                max_results=5,
                tweet_fields=["id", "text", "created_at"]
            )

            if tweets.data:
                for tweet in tweets.data:
                    if is_aceh_related(tweet.text):
                        try:
                            client.retweet(tweet.id)
                            save_for_digest(tweet.text)
                            print(f"Retweeted {tweet.id} from {username}")
                        except Exception as e:
                            print("Retweet error:", e)

                last_seen[username] = tweets.data[0].id

        except Exception as e:
            print(f"Error fetching tweets from {username}: {e}")

    # Save updated last seen
    with open(LAST_SEEN_FILE, "w") as f:
        json.dump(last_seen, f)


if __name__ == "__main__":
    main()
