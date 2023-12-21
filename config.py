import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_GROUP = os.environ.get("TELEGRAM_GROUP")
DEBUG = os.environ.get("DEBUG")
FILE_BANNED = "./files/banned.txt"
FILE_WHITELIST = "./files/whitelist.txt"