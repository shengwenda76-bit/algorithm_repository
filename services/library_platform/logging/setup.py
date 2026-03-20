import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path

from services.library_platform.settings import settings

def setup_logging():
    log_file_path = settings.get_log_file_path
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file_path)
    os.makedirs(log_dir, exist_ok=True)
    
    # Set default level
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
        
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (daily rotation)
    file_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when="midnight",
        backupCount=settings.LOG_BACKUP_DAYS,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logging.info("Logging configured successfully.")

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
