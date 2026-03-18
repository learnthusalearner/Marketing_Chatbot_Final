import time
from pymongo import MongoClient, errors
from pymongo.errors import BulkWriteError
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from utils.logger import logger

class MongoDBClient:
    def __init__(self):
        self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]
        self.processed_files = self.db["processed_files"]
        
        # Initialize indexes for duplication prevention
        self._ensure_indexes()

    def _ensure_indexes(self):
        try:
            # Ensure unique index on hash to prevent duplicate rows
            self.collection.create_index("row_hash", unique=True)
            # Ensure unique index on filename to prevent duplicate file processing
            self.processed_files.create_index("source_file", unique=True)
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")

    def is_file_processed(self, filename: str) -> bool:
        """Check if a file has already been processed successfully."""
        try:
            return self.processed_files.find_one({"source_file": filename}) is not None
        except Exception as e:
            logger.error(f"Error checking processed file status: {e}")
            return False

    def mark_file_processed(self, filename: str):
        """Mark a file as successfully processed."""
        try:
            self.processed_files.insert_one({
                "source_file": filename, 
                "processed_at": time.time()
            })
        except errors.DuplicateKeyError:
            pass  # Already marked
        except Exception as e:
            logger.error(f"Error marking file as processed: {e}")

    def insert_data(self, data: list, retries=3) -> int:
        """Insert records with chunking, retry logic, and duplicate handling."""
        if not data:
            return 0
            
        for attempt in range(retries):
            try:
                # Use ordered=False to continue inserting even if some fail (e.g., duplicates)
                result = self.collection.insert_many(data, ordered=False)
                return len(result.inserted_ids)
            except BulkWriteError as bwe:
                # Handle duplicate keys (Code 11000) gracefully
                duplicates = sum(1 for err in bwe.details['writeErrors'] if err['code'] == 11000)
                inserted = bwe.details['nInserted']
                logger.info(f"DB Insert: {inserted} rows added. Skipped {duplicates} duplicate rows.")
                return inserted
            except errors.ConnectionFailure as e:
                logger.error(f"DB connection failed (Attempt {attempt+1}/{retries}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logger.error(f"Unexpected DB error: {e}")
                if attempt == retries - 1:
                    raise
        return 0