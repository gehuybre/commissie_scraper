# config.py
from datetime import datetime, timedelta
import os

# === Base Directories ===
# Set BASE_DIR to the parent directory of this file.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Create directories if they do not exist.
os.makedirs(DATA_DIR, exist_ok=True)

# === Date Configuration ===
# Calculate date range for the past 7 days (including today).
today = datetime.today()
start_date = today - timedelta(days=7)
end_date = today

# Use start_date as unique identifier for this run.
RUN_DATE = start_date.strftime('%Y-%m-%d')

LAST_7_DAYS_START = start_date.strftime('%Y-%m-%d')
LAST_7_DAYS_END = end_date.strftime('%Y-%m-%d')

# === Commission Configurations ===
# Each commission has:
# - name: Used for file naming and directory structure
# - id: The commission ID used in the vlaamsparlement.be URL
# - description: A description of the commission (optional)
COMMISSIONS = {
    "omgeving": {
        "name": "omgeving",
        "id": "1832495",
        "description": "Commissie voor Leefmilieu, Natuur, Ruimtelijke Ordening en Energie"
    },
        "wonen": {
        "name": "wonen",
        "id": "1832499",
        "description": "Commissie voor Wonen, Toerisme, Energie en Klimaat"
    },
            "werk": {
        "name": "werk",
        "id": "1832493",
        "description": "Commissie voor Economie, Werk, Sociale Economie, Wetenschap en Innovatie"
    },
    # Example of how to add another commission:
    # "onderwijs": {
    #     "name": "onderwijs",
    #     "id": "1832496",  # Replace with actual ID
    #     "description": "Commissie voor Onderwijs"
    # },
}

# === URL Template ===
BASE_COMMISSION_URL = "https://www.vlaamsparlement.be/nl/parlementair-werk/plenaire-vergadering/vergaderingen?period_search=custom&type={commission_id}&start_period={start_date}&end_period={end_date}"

# === File Path Generation ===
def get_commission_dir(commission_name):
    """Get the directory for a specific commission."""
    commission_dir = os.path.join(DATA_DIR, commission_name)
    os.makedirs(commission_dir, exist_ok=True)
    return commission_dir

def get_run_dir(commission_name):
    """Get the directory for the current run of a specific commission."""
    run_dir = os.path.join(get_commission_dir(commission_name), RUN_DATE)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir

def get_meetings_csv_path(commission_name):
    """Get path for meetings CSV file."""
    return os.path.join(get_run_dir(commission_name), f"{commission_name}_meetings.csv")

def get_content_csv_path(commission_name):
    """Get path for content CSV file."""
    return os.path.join(get_run_dir(commission_name), f"{commission_name}_content.csv")

# === Commission-specific URLs ===
def get_commission_url(commission):
    """Generate the URL for a specific commission."""
    return BASE_COMMISSION_URL.format(
        commission_id=commission["id"],
        start_date=LAST_7_DAYS_START,
        end_date=LAST_7_DAYS_END
    )

# === Base URLs for scrapers ===
BASE_MEETING_URL = "https://www.vlaamsparlement.be/nl/parlementair-werk/commissies/commissievergaderingen/"
BASE_QUESTIONS_URL = "https://www.vlaamsparlement.be/nl/parlementaire-documenten/vragen-en-interpellaties/"
BASE_URL_PREFIX = "https://www.vlaamsparlement.be/"