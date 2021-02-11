import os

# API settings
API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = f"http://ws.audioscrobbler.com/2.0/?api_key={API_KEY}&format=json"

# data lake settings
STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
CONTAINER_NAME = "scrobbledatacontainer"

# User download settings
PERIOD_START_UTS = "1606780800"
PERIOD_END_UTS = "1609372800"
SNOWBALL_STARTING_USER = "crawlingtar"  # "orenjitubasa"
USERS_CHUNK_SIZE = 10 #1000
MIN_TARGET_USERS = USERS_CHUNK_SIZE * 1
