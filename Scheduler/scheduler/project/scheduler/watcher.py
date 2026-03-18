import os
import time
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import WATCH_FOLDER, POLL_INTERVAL
from utils.logger import logger

class ExcelHandler(FileSystemEventHandler):
    def __init__(self, file_queue: queue.Queue):
        self.file_queue = file_queue

    def on_created(self, event):
        if not event.is_directory:
            ext = os.path.splitext(event.src_path)[1].lower()
            if ext in [".xlsx", ".xls"]:
                # Ignore hidden/temp files like ~$filename.xlsx
                if not os.path.basename(event.src_path).startswith("~$"):
                    logger.info(f"Target file detected: {event.src_path}")
                    self.file_queue.put(event.src_path)

class FolderWatcher:
    def __init__(self):
        self.queue = queue.Queue()
        self.observer = None

    def start(self):
        if not os.path.exists(WATCH_FOLDER):
            os.makedirs(WATCH_FOLDER)
            
        # Add pre-existing files to queue (files dropped before script started)
        for file in os.listdir(WATCH_FOLDER):
            ext = os.path.splitext(file)[1].lower()
            if ext in [".xlsx", ".xls"] and not file.startswith("~$"):
                full_path = os.path.join(WATCH_FOLDER, file)
                self.queue.put(full_path)

        # Setup Watchdog observer
        event_handler = ExcelHandler(self.queue)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=WATCH_FOLDER, recursive=False)
        self.observer.start()
        logger.info(f"Started folder observer on {WATCH_FOLDER}")

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        logger.info("Folder observer stopped.")

    def get_files(self):
        """Yields files as they arrive in the queue."""
        while True:
            try:
                # Use a timeout so we can exit gracefully
                file_path = self.queue.get(timeout=POLL_INTERVAL)
                yield file_path
            except queue.Empty:
                continue