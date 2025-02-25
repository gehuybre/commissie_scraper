# speeches_scraper.py
import os
import csv
import logging
import pandas as pd
from bs4 import BeautifulSoup
from utils import safe_get_text, write_csv, append_to_csv
from request_helper import make_request

class SpeechesScraper:
    def __init__(self, input_csv, output_csv, base_url_prefix):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.base_url_prefix = base_url_prefix
        self.output_data = []
    
    def scrape(self):
        if not os.path.exists(self.input_csv):
            logging.error("Input CSV file not found: %s", self.input_csv)
            return []
        
        # Read the content CSV to get question links
        try:
            df = pd.read_csv(self.input_csv)
            # Filter for question content types that have links
            if 'content_type' in df.columns and 'question' in df['content_type'].values:
                questions_df = df[df['content_type'] == 'question']
                # Get unique links to process
                links_to_process = []
                for _, row in questions_df.iterrows():
                    if 'link' in row and row['link'] and isinstance(row['link'], str):
                        links_to_process.append(row['link'])
                links_to_process = list(set(links_to_process))  # Remove duplicates
            else:
                links_to_process = []
                logging.warning("No question data found in content CSV")
        except Exception as e:
            logging.error("Error reading input CSV %s: %s", self.input_csv, e)
            return []
        
        if not links_to_process:
            logging.warning("No links found to process in %s", self.input_csv)
            return []
        
        # Scrape speeches for each question link
        for link in links_to_process:
            full_url = self.base_url_prefix + link if not link.startswith('http') else link
            logging.info("Scraping speeches from page: %s", full_url)
            
            # Use the request helper to make the request with a delay
            response = make_request(full_url)
            if not response:
                continue  # Skip this link if request failed
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract title from header
            titel = ""
            header = soup.find("header", class_="card__header")
            if header:
                p_title = header.find("p", class_="card__title")
                if p_title:
                    hidden_span = p_title.find("span", class_="visually-hidden")
                    if hidden_span:
                        hidden_span.decompose()
                    titel = safe_get_text(p_title)
            if not titel:
                logging.warning("No titel found on %s", full_url)
            
            datum = ""
            datum_elem = soup.find("date", class_="meeting-header__date-full")
            if datum_elem:
                datum = safe_get_text(datum_elem)
            if not datum:
                logging.warning("No datum found on %s", full_url)
            
            # Find question ID to link speeches back to the question
            question_id = ""
            for _, row in questions_df.iterrows():
                if row.get('link') == link:
                    question_id = row.get('ID', '')
                    break
            
            speeches_container = soup.find("div", class_="meeting-speeches__list")
            if not speeches_container:
                logging.warning("No meeting speeches container found on %s; skipping speeches.", full_url)
                continue
            speeches = speeches_container.find_all("div", class_=lambda x: x and "meeting-speech" in x)
            if not speeches:
                logging.info("No meeting speeches found on %s.", full_url)
                continue
            
            for speech in speeches:
                spreker = ""
                title_div = speech.find("div", class_="meeting-speech__title")
                if title_div:
                    a_elem = title_div.find("a")
                    spreker = safe_get_text(a_elem) if a_elem else safe_get_text(title_div)
                sprekertekst = ""
                value_div = speech.find("div", class_="meeting-speech__value")
                if value_div:
                    sprekertekst = value_div.get_text(" ", strip=True)
                self.output_data.append({
                    "titel": titel,
                    "spreker": spreker,
                    "sprekertekst": sprekertekst,
                    "datum": datum,
                    "question_id": question_id,
                    "content_type": "speech",
                    "speech_link": full_url
                })
        
        if self.output_data:
            # Check if the output file already exists
            file_exists = os.path.exists(self.output_csv)
            
            if file_exists:
                try:
                    # Read existing headers to match columns
                    existing_df = pd.read_csv(self.output_csv)
                    
                    # Ensure all necessary columns exist in the DataFrame
                    required_columns = ["titel", "spreker", "sprekertekst", "datum", 
                                       "question_id", "content_type", "speech_link", "commission"]
                    
                    # Get the existing columns
                    existing_columns = existing_df.columns.tolist()
                    
                    # Check if we need to add any columns
                    for col in required_columns:
                        if col not in existing_columns:
                            existing_df[col] = ""  # Add empty column
                    
                    # Save the updated DataFrame with all necessary columns
                    existing_df.to_csv(self.output_csv, index=False)
                    
                    # Now update fieldnames to match the file
                    fieldnames = existing_df.columns.tolist()
                    mode = 'a'
                    write_header = False
                except Exception as e:
                    logging.error("Error updating CSV structure: %s", e)
                    # If we can't modify the existing file, create a new one with all needed columns
                    fieldnames = ["titel", "spreker", "sprekertekst", "datum", 
                                 "question_id", "content_type", "speech_link", "commission"]
                    mode = 'w'
                    write_header = True
            else:
                # If file doesn't exist, create it
                mode = 'w'
                fieldnames = ["titel", "spreker", "sprekertekst", "datum", 
                             "question_id", "content_type", "speech_link", "commission"]
                write_header = True
            
            # Write to CSV
            with open(self.output_csv, mode, newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                writer.writerows(self.output_data)
            
            logging.info("Saved %d speeches to %s", len(self.output_data), self.output_csv)
        else:
            logging.info("No speeches data scraped.")
        
        return self.output_data

if __name__ == '__main__':
    import config
    commission_name = "omgeving"  # Example commission
    content_csv = config.get_content_csv_path(commission_name)
    base_url_prefix = "https://www.vlaamsparlement.be/"
    scraper = SpeechesScraper(content_csv, content_csv, base_url_prefix)
    scraper.scrape()