import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "file_ingestion")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "records")

WATCH_FOLDER = os.getenv("WATCH_FOLDER", "data/")
PROCESSED_FOLDER = os.getenv("PROCESSED_FOLDER", "processed/")
FAILED_FOLDER = os.getenv("FAILED_FOLDER", "failed/")

# Parse poll interval safely
try:
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))
except ValueError:
    POLL_INTERVAL = 5