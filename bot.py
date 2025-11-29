import tweepy
import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

# Authenticate using OAuth 1.0a (required for retweets)
auth = tweepy.OAuth1UserHandler(
    API_KEY,
    API_SECRET,
    ACCESS_TOKEN,
    ACCESS_SECRET
)

api = tweepy.API(auth)

def main():
    # Fetch latest tweets from @infoBMKG
    tweets = api.user_timeline(
        screen_name="infoBMKG",
        count=5,
        tweet_mode="extended"
    )

    for tweet in tweets:
        if not tweet.retweeted:
            try:
                api.retweet(tweet.id)
                print("Retweeted:", tweet.full_text[:80])
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    main()
