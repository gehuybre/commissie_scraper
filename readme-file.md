# Flemish Parliament Commission Scraper

## Project Overview

This project is a web scraping application designed to collect, process, and analyze data from the Flemish Parliament website (vlaamsparlement.be). The scraper collects information about committee meetings, parliamentary questions, interpellations, and speeches for various commissions.

The system is designed to be modular, allowing easy addition of new parliamentary commissions by simply updating the configuration.

## Features

- **Modular Design**: Easy to add new commissions without code changes
- **Organized Data Structure**: Data is stored by commission and date
- **Efficient Storage**: Data is consolidated into two CSV files per commission run
- **Complete Pipeline**: Automatically scrapes meeting data, agenda items, questions, and speeches

## Project Structure

```
commissie_scraper/
├── src/                  # Source code directory
│   ├── config.py         # Configuration settings and commission definitions
│   ├── main.py           # Main workflow orchestration
│   ├── utils.py          # Utility functions for web scraping and file handling
│   ├── scrapers.py       # Base scraper classes 
│   ├── agenda_scraper.py # Specialized scraper for meeting agendas
│   ├── questions_scraper.py # Specialized scraper for parliamentary questions
│   └── speeches_scraper.py  # Specialized scraper for meeting speeches
└── data/                 # Data directory (organized by commission)
    └── omgeving/         # Example commission directory
        └── YYYY-MM-DD/   # Date-based directories for each run
            ├── omgeving_meetings.csv   # Meeting and agenda data
            └── omgeving_content.csv    # Questions and speeches data
```

## File Descriptions

### Core Files

- **config.py**: Contains configuration settings, including commission definitions, URLs, and file path generators
- **main.py**: Orchestrates the entire workflow, running each step for each commission
- **utils.py**: Provides utility functions for web requests, HTML parsing, and CSV handling

### Scraper Files

- **scrapers.py**: Contains base scraper classes and the CommissionScraper for initial meeting data
- **agenda_scraper.py**: Scrapes detailed agenda information from each meeting
- **questions_scraper.py**: Scrapes questions and interpellations from meeting agenda items
- **speeches_scraper.py**: Scrapes speeches from meeting transcripts

## Data Flow

The scraping workflow follows these steps for each commission:

1. **Initial Scraping**: Collects basic meeting information from the main commission page
2. **Agenda Scraping**: Gets detailed agenda items for each meeting
3. **Questions Scraping**: Extracts parliamentary questions and interpellations
4. **Speeches Scraping**: Collects speeches from meeting transcripts
5. **Data Cleaning**: Processes the collected data, removing irrelevant entries

## Output Files

For each commission run, two CSV files are created:

1. **{commission}_meetings.csv**: Contains meeting metadata and agenda items
   - Meeting dates, titles, descriptions, IDs
   - Agenda items with document numbers and links

2. **{commission}_content.csv**: Contains all questions and speeches
   - Questions with titles and links
   - Speeches with speaker names, text, and dates

## How to Add a New Commission

To add a new commission, simply update the `COMMISSIONS` dictionary in `config.py`:

```python
COMMISSIONS = {
    "omgeving": {
        "name": "omgeving",
        "id": "1832495",
        "description": "Commissie voor Leefmilieu, Natuur, Ruimtelijke Ordening en Energie"
    },
    "new_commission": {
        "name": "new_commission",
        "id": "1234567",  # The commission ID from the vlaamsparlement.be URL
        "description": "Description of the new commission"
    }
}
```

The ID can be found in the URL of the commission page on the Flemish Parliament website:
`https://www.vlaamsparlement.be/nl/parlementair-werk/plenaire-vergadering/vergaderingen?period_search=custom&type=1832495&start_period=2023-01-01&end_period=2023-12-31`

In this example, `1832495` is the commission ID for "omgeving".

## Running the Scraper

To run the scraper, execute the main.py script:

```python
from src import main
main.main()
```

This will run the full workflow for all configured commissions, creating a new date-based directory for the current run.

## Dependencies

- Python 3.6+
- BeautifulSoup4
- Requests
- Pandas
