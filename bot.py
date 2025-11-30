import os
import tweepy
import time
from datetime import datetime, timedelta

# Authenticate using OAuth 1.0a (READ + WRITE)
auth = tweepy.OAuth1UserHandler(
    os.getenv("API_KEY"),
    os.getenv("API_SECRET"),
    os.getenv("ACCESS_TOKEN"),
    os.getenv("ACCESS_SECRET")
)

api = tweepy.API(auth)

# ------------------------------
# SOURCE ACCOUNTS
# ------------------------------
SOURCE_ACCOUNTS = [
    "infoBMKG",
    "BMKG_ACEH",
    "BMKG_Official",
    "BNPB_Indonesia",
    "BPBD_Aceh"
]

# ------------------------------
# KEYWORDS FOR ALL ACEH REGIONS
# ------------------------------
ACEH_KEYWORDS = [
    "aceh", "banda aceh", "sabang", "lhokseumawe", "langsa", "subulussalam",
    "aceh besar", "pidie", "pidie jaya", "aceh utara", "aceh timur",
    "aceh tamiang", "aceh tengah", "aceh tenggara", "aceh selatan",
    "aceh singkil", "aceh jaya", "aceh barat", "aceh barat daya",
    "gayo lues", "bener meriah", "nagan raya", "simeulue"
]

# ------------------------------
# HASHTAGS FOR VISIBILITY
# ------------------------------
HAS
