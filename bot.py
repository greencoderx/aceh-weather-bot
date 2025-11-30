import tweepy
import os
import time
import requests

### --- Setup Global Timeout for Tweepy --- ###
session = requests.Session()
session.request = requests.Session().request
session.timeout = 10  # 10 seconds timeout

### --- Setup Tweepy Client (Essential Tier Compatible) --- ###
client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET"),
    wait_on_rate_limit=True,
    session=session
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
