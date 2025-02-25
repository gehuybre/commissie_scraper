# questions_scraper.py
import os
import csv
import logging
import pandas as pd
from bs4 import BeautifulSoup
from utils import safe_get_text, write_csv
from request_helper import make_request

class QuestionsScraper:
    def __init__(self, input_csv, output_csv, base_url):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.base_url = base_url
        self.output_data = []
    
    def scrape(self):
        if not os.path.exists(self.input_csv):
            logging.error("Input CSV file not found: %s", self.input_csv)
            return []
        
        # Read the meetings CSV to get IDs of meetings/agenda items
        try:
            df = pd.read_csv(self.input_csv)
            
            # We're interested in the agenda items (if available) 
            # or the meeting IDs if no agenda items exist
            if 'data_type' in df.columns and 'agenda_item' in df['data_type'].values:
                # Filter for agenda items
                agenda_items = df[df['data_type'] == 'agenda_item']
                ids_to_process = agenda_items["ID"].dropna().astype(str).tolist()
            else:
                # No agenda items found, use all available IDs
                ids_to_process = df["ID"].dropna().astype(str).tolist()
        except Exception as e:
            logging.error("Error reading input CSV %s: %s", self.input_csv, e)
            return []
        
        if not ids_to_process:
            logging.warning("No IDs found to process in %s", self.input_csv)
            return []
        
        # Scrape question details for each ID
        for item_id in ids_to_process:
            url = self.base_url + item_id
            logging.info("Scraping question from URL: %s", url)
            
            # Use the request helper to make the request with a delay
            response = make_request(url)
            if not response:
                continue  # Skip this item if request failed
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content_div = soup.find("div", class_="page-layout__content")
            if not content_div:
                logging.warning("Could not find page content on %s; skipping.", url)
                continue
            
            subtitle_elem = content_div.find("h2", class_="page-subtitle")
            titel = safe_get_text(subtitle_elem)
            if not titel:
                logging.warning("No subtitle found on %s", url)
            
            report_link_elem = content_div.find("a", class_="button button-primary header-links-icon--report")
            link = report_link_elem.get("href", "").strip() if report_link_elem else ""
            new_id = link.rstrip('/').split('/')[-1] if link else ""
            
            self.output_data.append({
                "titel": titel,
                "link": link,
                "ID": new_id,
                "original_ID": item_id,
                "content_type": "question"
            })
        
        if self.output_data:
            # Check if the output file already exists
            file_exists = os.path.exists(self.output_csv)
            
            if file_exists:
                # If file exists, append to it
                mode = 'a'
                # Read existing headers
                existing_df = pd.read_csv(self.output_csv)
                fieldnames = existing_df.columns.tolist()
                write_header = False
            else:
                # If file doesn't exist, create it
                mode = 'w'
                fieldnames = ["titel", "link", "ID", "original_ID", "content_type", "commission"]
                write_header = True
            
            # Write to CSV
            with open(self.output_csv, mode, newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                writer.writerows(self.output_data)
            
            logging.info("Saved %d questions to %s", len(self.output_data), self.output_csv)
        else:
            logging.info("No questions data scraped.")
        
        return self.output_data

if __name__ == '__main__':
    import config
    commission_name = "omgeving"  # Example commission
    base_url = "https://www.vlaamsparlement.be/nl/parlementaire-documenten/vragen-en-interpellaties/"
    meetings_csv = config.get_meetings_csv_path(commission_name)
    content_csv = config.get_content_csv_path(commission_name)
    scraper = QuestionsScraper(meetings_csv, content_csv, base_url)
    scraper.scrape()