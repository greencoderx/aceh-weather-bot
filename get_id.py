import tweepy
import os

BEARER_TOKEN = os.getenv("BEARER_TOKEN")

client = tweepy.Client(bearer_token=BEARER_TOKEN)

user = client.get_user(username="infoBMKG")
print("User ID:", user.data.id)
