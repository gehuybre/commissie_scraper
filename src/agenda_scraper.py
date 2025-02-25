# agenda_scraper.py
import os
import csv
import logging
import pandas as pd
from bs4 import BeautifulSoup
from utils import safe_get_text, write_csv
from request_helper import make_request

class AgendaScraper:
    def __init__(self, input_csv, output_csv, base_meeting_url):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.base_meeting_url = base_meeting_url
        self.all_data = []
    
    def scrape(self):
        if not os.path.exists(self.input_csv):
            logging.error("Input CSV file not found: %s", self.input_csv)
            return []
        
        # Read the existing CSV to get meeting IDs
        try:
            df = pd.read_csv(self.input_csv)
            meeting_ids = df["ID"].dropna().astype(str).tolist()
        except Exception as e:
            logging.error("Error reading input CSV %s: %s", self.input_csv, e)
            return []
        
        if not meeting_ids:
            logging.warning("No meeting IDs found in %s", self.input_csv)
            return []
        
        # Scrape agenda items for each meeting
        for meeting_id in meeting_ids:
            meeting_url = self.base_meeting_url + meeting_id
            logging.info("Scraping meeting details from: %s", meeting_url)
            
            # Use the request helper to make the request with a delay
            response = make_request(meeting_url)
            if not response:
                continue  # Skip this meeting if request failed
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find agenda cards with the required classes
            cards = soup.find_all("article", class_=lambda x: x and all(cls in x.split() for cls in ["card", "document-type--report", "document-subtype--journal_item"]))
            if not cards:
                logging.info("No matching cards found in meeting %s", meeting_id)
                continue
            
            for card in cards:
                card_tag = safe_get_text(card.find("h4", class_="card__tag"))
                card_title = safe_get_text(card.find("p", class_="card__title"))
                card_doc_num = safe_get_text(card.find("span", class_="card__document-number"))
                card_author = safe_get_text(card.find("p", class_="card__author"))
                internal_link_elem = card.select_one("li.card__link.card__link-view.internal a")
                verslag_link = internal_link_elem.get("href", "").strip() if internal_link_elem else ""
                extracted_id = verslag_link.rstrip('/').split('/')[-1] if verslag_link else ""
                self.all_data.append({
                    "meeting_ID": meeting_id,
                    "card__tag": card_tag,
                    "card__title": card_title,
                    "card__document_number": card_doc_num,
                    "card__author": card_author,
                    "verslag_link": verslag_link,
                    "ID": extracted_id
                })
        
        if self.all_data:
            # Now we need to update the existing meetings CSV with agenda info
            # We'll keep the original format but add new columns for agenda items
            
            # Read the existing meetings data
            meetings_df = pd.read_csv(self.input_csv)
            
            # Create a dataframe from the scraped agenda data
            agenda_df = pd.DataFrame(self.all_data)
            
            # Add a flag column to indicate this is agenda data
            agenda_df['data_type'] = 'agenda_item'
            
            # Combine the original meetings with the agenda items
            # This approach preserves all the original meeting data
            combined_df = pd.concat([meetings_df, agenda_df], ignore_index=True)
            
            # Write the combined data back to the CSV
            combined_df.to_csv(self.output_csv, index=False)
            logging.info("Updated meetings CSV with %d agenda items", len(self.all_data))
        else:
            logging.info("No agenda items scraped.")
        
        return self.all_data

if __name__ == '__main__':
    import config
    commission_name = "omgeving"  # Example commission
    base_meeting_url = "https://www.vlaamsparlement.be/nl/parlementair-werk/commissies/commissievergaderingen/"
    meetings_csv = config.get_meetings_csv_path(commission_name)
    scraper = AgendaScraper(meetings_csv, meetings_csv, base_meeting_url)
    scraper.scrape()