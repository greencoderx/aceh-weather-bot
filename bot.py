import tweepy
import os
import time

### --- Setup API Client --- ###
client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET"),
    wait_on_rate_limit=True,
    request_timeout=10  # prevent hanging
)

### --- Source Accounts (Usernames) --- ###
SOURCE_USERNAMES = [
    "infoBMKG",
    "BMKG_ACEH",
    "BMKG_Official",
    "BNPB_Indonesia",
    "BPBD_Aceh"
]

### --- Aceh Keywords --- ###
ACEH_KEYWORDS = [
    "Aceh", "Banda Aceh", "Aceh Besar", "Pidie", "Pidie Jaya", "Bireuen",
    "Lhokseumawe", "Aceh Utara", "Aceh Timur", "Langsa", "Aceh Tamiang",
    "Gayo Lues", "Aceh Tengah", "Takengon", "Aceh Tenggara", "Subulussalam",
    "Aceh Selatan", "Tapaktuan", "Aceh Singkil", "Simeulue", "Meulaboh",
    "Aceh Barat", "Nagan Raya", "Aceh Jaya", "Sabang"
]

### --- Hashtags --- ###
HASHTAGS = "#AcehWeather #CuacaAceh #BMKG #PeringatanDini"

### --- Retry Handler --- ###
def safe_api_call(func, *args, **kwargs):
    for attempt in range(3):  # 3 retries
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[WARN] API error: {e} (attempt {attempt+1}/3)", flush=True)
            time.sleep(2)
    print("[ERROR] Failed after 3 retries.", flush=True)
    return None

### --- Convert usernames → user IDs --- ###
def get_user_ids():
    ids = []
    for username in SOURCE_USERNAMES:
        print(f"[INFO] Fetching ID for {username}", flush=True)
        user = safe_api_call(client.get_user, username=username)
        if user and user.data:
            ids.append(str(user.data.id))
            print(f"  → ID: {user.data.id}", flush=True)
        else:
            print(f"[ERROR] Unable to get ID for {username}", flush=True)
    return ids

### --- Check Aceh relevance --- ###
def is_aceh_related(text):
    return any(k.lower() in text.lower() for k in ACEH_KEYWORDS)

### --- Main Bot Logic --- ###
def run_bot():
    print("[INFO] Starting Aceh Weather Bot v2", flush=True)

    source_ids = get_user_ids()
    if not source_ids:
        print("[FATAL] No source IDs found. Exiting.", flush=True)
        return

    for user_id in source_ids:
        print(f"\n[INFO] Fetching tweets for user ID: {user_id}", flush=True)

        tweets = safe_api_call(
            client.get_users_tweets,
            id=user_id,
            max_results=5,
            tweet_fields=["created_at", "text"]
        )

        if not tweets or not tweets.data:
            print("[INFO] No tweets found / API block.", flush=True)
            continue

        for tweet in tweets.data:
            text = tweet.text
            print(f"  → Checking tweet: {text[:50]}...", flush=True)

            if not is_aceh_related(text):
                continue

            print("    ✓ Aceh-related tweet found.", flush=True)

            # Attempt retweet
            ret = safe_api_call(
                client.retweet,
                tweet_id=tweet.id
            )

            if ret:
                print("    ✓ Retweeted successfully!", flush=True)
            else:
                print("    ✗ Failed to retweet.", flush=True)

    print("\n[INFO] Bot finished execution.", flush=True)

### --- Execute Bot --- ###
if __name__ == "__main__":
    run_bot()