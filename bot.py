import tweepy
import os

# Load secrets from GitHub Actions
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")  # new required for v2

# Authenticate v2 client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Numeric user ID of @infoBMKG
# You can find this via: https://tweeterid.com
INFO_BMKG_ID = "1101026756120193025"  # example ID

def main():
    # Get the 5 most recent tweets
    response = client.get_users_tweets(
        id=INFO_BMKG_ID,
        max_results=5,
        tweet_fields=["id", "text"]
    )

    if response.data is None:
        print("No tweets found")
        return

    for tweet in response.data:
        try:
            # Retweet
            client.retweet(tweet.id)
            print("Retweeted:", tweet.text[:80])
        except tweepy.TweepyException as e:
            print("Error retweeting:", e)

if __name__ == "__main__":
    main()
