import logging
import sys

def get_logger(name="scheduler_service"):
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if already initialized
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        
        # Standard output handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
    return logger

# Singleton instance exported for use
logger = get_logger()