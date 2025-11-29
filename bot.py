import tweepy
import os

# X API keys from GitHub secrets
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

# Authenticate
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Trusted sources
SOURCE_ACCOUNTS = [
    "infoBMKG",
    "BMKG_ACEH",
    "BMKG_Official",
    "BNPB_Indonesia",
    "BPBD_Aceh",
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

def is_aceh_related(text):
    return any(k.lower() in text.lower() for k in KEYWORDS)

def save_for_digest(tweet_text):
    with open(DAILY_FILE, "a", encoding="utf-8") as f:
        f.write(tweet_text + "\n---\n")

def main():
    for account in SOURCE_ACCOUNTS:
        try:
            tweets = api.user_timeline(
                screen_name=account,
                count=5,
                tweet_mode="extended"
            )

            for tweet in tweets:
                if not tweet.retweeted and is_aceh_related(tweet.full_text):
                    try:
                        api.retweet(tweet.id)
                        save_for_digest(tweet.full_text)
                        print(f"Retweeted from {account}:", tweet.full_text[:80])
                    except Exception as e:
                        print("Error retweeting:", e)
        except Exception as e:
            print(f"Error fetching tweets from {account}:", e)

if __name__ == "__main__":
    main()