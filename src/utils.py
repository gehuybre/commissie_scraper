# utils.py
import os
import csv
import logging
import requests
import time
import random
from bs4 import BeautifulSoup

# Configure logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def safe_get_text(tag, default=""):
    """Return the stripped text of a BeautifulSoup tag, or a default value."""
    return tag.get_text(strip=True) if tag else default

def load_soup(url, session=None):
    """Fetch a URL and return a BeautifulSoup object, or None on error."""
    # Add a random delay between requests to be respectful to the server
    time.sleep(random.uniform(1, 3))
    
    sess = session or requests
    logging.info("Fetching URL: %s", url)
    
    # Add a proper user-agent header
    headers = {
        'User-Agent': 'Vlaams Parlement Scraper/1.0 (Educational/Research Use)',
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        response = sess.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error("Error fetching %s: %s", url, e)
        return None
    return BeautifulSoup(response.content, 'html.parser')

def write_csv(output_path, data, fieldnames):
    """Write data (a list of dictionaries) to a CSV file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    logging.info("Data successfully saved to: %s", output_path)

def append_to_csv(output_path, data, fieldnames=None):
    """Append data to an existing CSV file or create a new one."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    file_exists = os.path.exists(output_path)
    if file_exists and not fieldnames:
        # Read existing fieldnames if not provided
        with open(output_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
    
    mode = 'a' if file_exists else 'w'
    with open(output_path, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)
    
    logging.info("%s %d rows to %s", 
                "Appended" if file_exists else "Wrote", 
                len(data), 
                output_path)
    return True

def get_commission_directory(base_dir, commission_name):
    """Get the directory for a specific commission, creating it if needed."""
    commission_dir = os.path.join(base_dir, commission_name)
    os.makedirs(commission_dir, exist_ok=True)
    return commission_dir

def get_run_directory(base_dir, commission_name, run_date):
    """Get the directory for a specific commission run, creating it if needed."""
    run_dir = os.path.join(get_commission_directory(base_dir, commission_name), run_date)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir