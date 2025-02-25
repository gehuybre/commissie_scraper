# error_handler.py
import os
import sys
import logging
import traceback
from datetime import datetime

def setup_error_logging():
    """
    Set up error logging to both console and file
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Set up file handler with today's date
    today = datetime.today().strftime('%Y-%m-%d')
    log_file = f'logs/scraper_{today}.log'
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log start of script
    logging.info("-------------------------------------------")
    logging.info("Starting Vlaams Parlement scraper")
    logging.info("-------------------------------------------")

def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler to log uncaught exceptions
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't override KeyboardInterrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logging.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

def init():
    """
    Initialize error handling
    """
    setup_error_logging()
    
    # Set up global exception handler
    sys.excepthook = handle_exception