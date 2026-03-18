import os
import sys
import shutil
import signal
import time
from scheduler.watcher import FolderWatcher
from services.file_processor import FileProcessor
from db.mongo_client import MongoDBClient
from utils.logger import logger
from config import WATCH_FOLDER, PROCESSED_FOLDER, FAILED_FOLDER

# Global running flag for graceful termination
running = True

def handle_shutdown(signum, frame):
    global running
    logger.info("Shutdown signal received. Wrapping up...")
    running = False

def ensure_folders():
    for folder in [WATCH_FOLDER, PROCESSED_FOLDER, FAILED_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)

def move_file(file_path, dest_folder):
    try:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(dest_folder, filename)
        
        # Override file if it exists in dest
        if os.path.exists(dest_path):
            os.remove(dest_path)
            
        shutil.move(file_path, dest_path)
        logger.info(f"Moved {filename} to {dest_folder}")
    except Exception as e:
        logger.error(f"Failed to move {file_path} to {dest_folder}: {e}")

def run():
    global running
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    ensure_folders()
    
    watcher = FolderWatcher()
    processor = FileProcessor()
    
    try:
        db = MongoDBClient()
    except Exception as e:
        logger.critical(f"MongoDB connection failed: {e}")
        sys.exit(1)

    watcher.start()
    logger.info("File Ingestion System running. Waiting for files...")

    try:
        for file_path in watcher.get_files():
            if not running:
                break
                
            filename = os.path.basename(file_path)
            
            # Brief delay to ensure large files are completely written to disk
            time.sleep(1)

            logger.info(f"Initiating processing for: {filename}")

            if db.is_file_processed(filename):
                logger.warning(f"File {filename} has already been processed previously. Skipping.")
                move_file(file_path, PROCESSED_FOLDER)
                continue

            try:
                data = processor.process(file_path)
                if data:
                    inserted = db.insert_data(data)
                    logger.info(f"Successfully processed {filename}. {inserted} records inserted.")
                else:
                    logger.info(f"No valid records found in {filename}.")
                
                db.mark_file_processed(filename)
                move_file(file_path, PROCESSED_FOLDER)

            except Exception as e:
                logger.error(f"Error processing {filename}: {e}", exc_info=False)
                move_file(file_path, FAILED_FOLDER)
                
    except Exception as e:
        logger.critical(f"Critical execution error: {e}")
    finally:
        watcher.stop()
        logger.info("Shutdown routine complete. Exiting.")

if __name__ == "__main__":
    run()