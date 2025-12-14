import tweepy
import os

# Load secrets from GitHub Actions
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")  # required for v2

# Authenticate v2 client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

TARGET_USERNAME = "infoBMKG"

def get_user_id(username):
    """Fetch numeric user ID for the given username"""
    try:
        user = client.get_user(username=username)
        return user.data.id
    except Exception as e:
        print("Error fetching user ID:", e)
        return None

def main():
    user_id = get_user_id(TARGET_USERNAME)
    if not user_id:
        print("Cannot fetch user ID. Exiting.")
        return

    # Get recent tweets from the user
    try:
        response = client.get_users_tweets(
            id=user_id,
            max_results=5,
            tweet_fields=["id", "text"]
        )
    except Exception as e:
        print("Error fetching tweets:", e)
        return

    if not response.data:
        print("No tweets found")
        return

    for tweet in response.data:
        text = tweet.text
        if "Aceh" in text or "aceh" in text:
            try:
                client.retweet(tweet.id)
                print("Retweeted:", text[:80])
            except tweepy.TweepyException as e:
                if "You have already retweeted this Tweet" in str(e):
                    print("Already retweeted:", text[:80])
                else:
                    print("Error retweeting:", e)
        else:
            print("Skipped tweet (not Aceh-related):", text[:80])

if __name__ == "__main__":
    main()
