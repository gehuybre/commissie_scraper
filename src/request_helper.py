# request_helper.py
import requests
import time
import random
import logging

def make_request(url):
    """
    Make an HTTP request with a random delay and proper headers.
    
    Args:
        url: The URL to request
        
    Returns:
        Response object on success, None on failure
    """
    # Add a random delay between requests to be respectful to the server
    time.sleep(random.uniform(1, 3))
    
    # Add a proper user-agent header
    headers = {
        'User-Agent': 'Vlaams Parlement Scraper/1.0 (Educational/Research Use)',
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    logging.info("Fetching URL: %s", url)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logging.error("Failed to retrieve %s: %s", url, e)
        return None