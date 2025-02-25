# clean_content_csv.py
import os
import pandas as pd
import logging
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def clean_content_csv(csv_path):
    """
    Clean the content CSV file by:
    1. Removing rows where 'spreker' equals 'De voorzitter'
    2. Removing rows where 'sprekertekst' is blank
    
    Args:
        csv_path: Path to the content CSV file
    
    Returns:
        int: Number of rows removed
    """
    logging.info(f"Cleaning CSV file: {csv_path}")
    
    try:
        # Load the CSV
        df = pd.read_csv(csv_path)
        
        # Skip if empty
        if df.empty:
            logging.warning(f"CSV file is empty: {csv_path}")
            return 0
        
        # Store original row count
        original_count = len(df)
        
        # Filter out rows with 'De voorzitter' as speaker
        # First check if 'spreker' column exists
        if 'spreker' in df.columns:
            df = df[df['spreker'] != 'De voorzitter']
        
        # Filter out rows with blank speaker text
        # First check if 'sprekertekst' column exists
        if 'sprekertekst' in df.columns:
            # Filter out rows where sprekertekst is NaN, empty string, or only whitespace
            df = df[~df['sprekertekst'].isna() & 
                   (df['sprekertekst'].astype(str).str.strip() != '')]
        
        # Calculate rows removed
        rows_removed = original_count - len(df)
        
        # Save back to the same file
        df.to_csv(csv_path, index=False)
        logging.info(f"Cleaned content data saved ({rows_removed} rows removed)")
        
        return rows_removed
    
    except Exception as e:
        logging.error(f"Error cleaning content data: {e}")
        return 0

def clean_all_content_files(data_dir):
    """
    Find and clean all content CSV files in the data directory.
    
    Args:
        data_dir: Base directory containing all commission data
    
    Returns:
        int: Total number of files processed
    """
    # Find all files ending with _content.csv in the data directory and its subdirectories
    content_files = glob.glob(os.path.join(data_dir, '**', '*_content.csv'), recursive=True)
    
    if not content_files:
        logging.warning(f"No content CSV files found in {data_dir}")
        return 0
    
    total_files = 0
    total_rows_removed = 0
    
    for file_path in content_files:
        rows_removed = clean_content_csv(file_path)
        total_rows_removed += rows_removed
        total_files += 1
    
    logging.info(f"Processed {total_files} content CSV files, removed {total_rows_removed} rows in total")
    return total_files

if __name__ == '__main__':
    import config
    data_dir = config.DATA_DIR
    clean_all_content_files(data_dir)