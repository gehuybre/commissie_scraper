# main.py
import os
import logging
import pandas as pd
import config
import error_handler  # Import the error handler

from utils import load_soup, write_csv, append_to_csv
from scrapers import CommissionScraper
from agenda_scraper import AgendaScraper
from questions_scraper import QuestionsScraper
from speeches_scraper import SpeechesScraper
from clean_content import clean_content_csv  # Import the cleaning function

# Initialize error handling
error_handler.init()

def run_commission_workflow(commission_config):
    """Run the full workflow for a single commission."""
    commission_name = commission_config["name"]
    logging.info("Starting workflow for commission: %s", commission_name)
    
    # Get file paths for this commission
    meetings_csv = config.get_meetings_csv_path(commission_name)
    content_csv = config.get_content_csv_path(commission_name)
    
    # Step 1: Initial scraping to get meeting IDs
    meetings_data = run_initial_scraping(commission_config, meetings_csv)
    if not meetings_data:
        logging.error("Failed to get initial meeting data for %s. Aborting workflow.", commission_name)
        return False
    
    # Step 2: Scrape detailed agenda information for each meeting
    run_agenda_scraper(commission_name, meetings_csv)
    
    # Step 3: Scrape questions and interpellations for each meeting
    questions_data = run_questions_scraper(commission_name, meetings_csv, content_csv)
    if not questions_data:
        logging.warning("No questions data found for %s", commission_name)
    
    # Step 4: Scrape speeches from each meeting
    run_speeches_scraper(commission_name, content_csv)
    
    # Step 5: Clean content data - improved version using the imported function
    if os.path.exists(content_csv):
        rows_removed = clean_content_csv(content_csv)
        logging.info("Content cleaning completed for %s. Removed %d rows.", commission_name, rows_removed)
    else:
        logging.warning("Content CSV file not found for %s. Skipping cleaning step.", commission_name)
    
    logging.info("Workflow for commission %s completed successfully.", commission_name)
    return True


def run_initial_scraping(commission_config, output_csv):
    """Scrape the main page and create the basic meetings CSV file."""
    commission_name = commission_config["name"]
    url = config.get_commission_url(commission_config)
    
    logging.info("Scraping initial data for commission %s from URL: %s", commission_name, url)
    soup = load_soup(url)
    if not soup:
        logging.error("Failed to load webpage for commission %s", commission_name)
        return False
    
    scraper = CommissionScraper(soup)
    scraped_data, fieldnames = scraper.scrape()
    
    if not scraped_data:
        logging.warning("No meetings found for commission %s", commission_name)
        return False
    
    # Add commission name to the data
    for item in scraped_data:
        item['commission'] = commission_name
    
    write_csv(output_csv, scraped_data, fieldnames + ['commission'])
    logging.info("Saved %d meetings for commission %s to %s", 
                len(scraped_data), commission_name, output_csv)
    return scraped_data


def run_agenda_scraper(commission_name, meetings_csv):
    """Run the agenda scraper for a specific commission and update the meetings CSV."""
    logging.info("Running agenda scraper for commission: %s", commission_name)
    
    scraper = AgendaScraper(
        input_csv=meetings_csv,
        output_csv=meetings_csv,  # We're updating the same file
        base_meeting_url=config.BASE_MEETING_URL
    )
    scraper.scrape()
    logging.info("Agenda scraping for commission %s completed.", commission_name)


def run_questions_scraper(commission_name, meetings_csv, content_csv):
    """Run the questions scraper for a specific commission and save to content CSV."""
    logging.info("Running questions scraper for commission: %s", commission_name)
    
    # Modified QuestionsScraper to handle the consolidated file approach
    scraper = QuestionsScraper(
        input_csv=meetings_csv,
        output_csv=content_csv,
        base_url=config.BASE_QUESTIONS_URL
    )
    questions_data = scraper.scrape()
    
    # Add commission name to each question
    if questions_data:
        for item in questions_data:
            item['commission'] = commission_name
            item['content_type'] = 'question'
    
    logging.info("Questions scraping for commission %s completed.", commission_name)
    return questions_data


def run_speeches_scraper(commission_name, content_csv):
    """Run the speeches scraper for a specific commission and append to content CSV."""
    logging.info("Running speeches scraper for commission: %s", commission_name)
    
    # Modified SpeechesScraper to handle the consolidated file approach
    scraper = SpeechesScraper(
        input_csv=content_csv,  # Reads questions from content_csv
        output_csv=content_csv,  # Appends speeches to content_csv
        base_url_prefix=config.BASE_URL_PREFIX
    )
    speeches_data = scraper.scrape()
    
    # Add commission name to each speech
    if speeches_data:
        for item in speeches_data:
            item['commission'] = commission_name
            item['content_type'] = 'speech'
    
    logging.info("Speeches scraping for commission %s completed.", commission_name)
    return speeches_data


def main():
    logging.info("Starting modular scraping workflow for all configured commissions.")
    logging.info(f"Data will be saved to: {config.DATA_DIR}")
    
    # Create data directory if it doesn't exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    success_count = 0
    failure_count = 0
    
    for commission_id, commission_config in config.COMMISSIONS.items():
        try:
            logging.info(f"Processing commission: {commission_id}")
            result = run_commission_workflow(commission_config)
            if result:
                success_count += 1
            else:
                failure_count += 1
        except Exception as e:
            logging.error(f"Error processing commission {commission_id}: {e}")
            failure_count += 1
    
    logging.info("Scraping workflow completed.")
    logging.info(f"Commissions processed successfully: {success_count}")
    logging.info(f"Commissions with errors: {failure_count}")
    
    if failure_count > 0:
        logging.warning("Some commissions had errors. Check the logs for details.")


if __name__ == '__main__':
    main()