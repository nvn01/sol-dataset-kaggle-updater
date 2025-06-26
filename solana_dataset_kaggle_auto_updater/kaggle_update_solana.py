import os
# Disable resumable uploads (helpful in CI environments)
os.environ["KAGGLE_API_NO_RESUME"] = "True"

import sys
import time
import shutil
import pandas as pd
from datetime import datetime
from binance.client import Client
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

# Load environment variables
load_dotenv()

KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
KAGGLE_KEY = os.getenv("KAGGLE_KEY")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Configure proxy settings (will be used for Binance API calls)
proxies = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY')
}

def create_binance_client(max_retries=3):
    """Create Binance client with retry logic."""
    local_proxies = {
        'http': os.getenv('HTTP_PROXY'),
        'https': os.getenv('HTTPS_PROXY')
    }
    
    for attempt in range(max_retries):
        try:
            client = Client(
                BINANCE_API_KEY, 
                BINANCE_API_SECRET,
                {
                    'proxies': local_proxies,
                    'timeout': 30,
                    'verify': True
                }
            )
            # Test the connection
            client.ping()
            print("Successfully connected to Binance API")
            return client
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                print("Waiting 10 seconds before retry...")
                time.sleep(10)
                os.system('sudo service tor restart')
                time.sleep(5)
            else:
                raise

# Initialize Binance client
client = create_binance_client()

# Base directory of the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
NEW_DATA_FOLDER = os.path.join(BASE_DIR, "new_data")
MERGED_FOLDER = os.path.join(BASE_DIR, "merged_data")  # New folder for merged files

def clean_folder(folder_path):
    """Clean the specified folder."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        return
    
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print(f"Cleaned folder: {folder_path}")

def download_kaggle_dataset(dataset_slug, output_dir):
    """Download the dataset and metadata from Kaggle."""
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(dataset_slug, path=output_dir, unzip=True)
    api.dataset_metadata(dataset_slug, path=output_dir)
    print(f"Dataset and metadata downloaded to {output_dir}")

def fetch_binance_data(symbol, interval, start_date, end_date, output_file, max_retries=3):
    """Fetch historical data from Binance with retry logic."""
    for attempt in range(max_retries):
        try:
            client = create_binance_client()
            klines = client.get_historical_klines(symbol, interval, start_date, end_date)
            columns = [
                'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
                'Close time', 'Quote asset volume', 'Number of trades',
                'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
            ]
            df = pd.DataFrame(klines, columns=columns)
            df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
            df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')
            df.to_csv(output_file, index=False)
            print(f"Fetched data saved to {output_file}")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                print("Waiting 20 seconds before retry...")
                time.sleep(20)
                os.system('sudo service tor restart')
                time.sleep(5)
            else:
                raise

def merge_datasets(existing_file, new_file, output_file):
    """Merge existing and new datasets."""
    existing_data = pd.read_csv(existing_file)
    new_data = pd.read_csv(new_file)

    # Ensure Open time is datetime
    existing_data['Open time'] = pd.to_datetime(existing_data['Open time'])
    new_data['Open time'] = pd.to_datetime(new_data['Open time'])

    merged_data = pd.concat([existing_data, new_data])
    merged_data.drop_duplicates(subset='Open time', inplace=True)
    merged_data.sort_values(by='Open time', inplace=True)
    merged_data.to_csv(output_file, index=False)
    print(f"Merged dataset saved to {output_file}")

def copy_metadata(src_folder, dest_folder):
    """Copy the metadata file to the destination folder."""
    import json
    
    # Create a metadata file for Solana dataset
    metadata = {
        "title": "Solana Price Data Binance API (2020–Now)",
        "id": "novandraanugrah/solana-price-data-binance-api-2020now",
        "licenses": [{"name": "CC BY 4.0"}]
    }
    
    metadata_file = os.path.join(dest_folder, "dataset-metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Created metadata file at {metadata_file}")

def upload_to_kaggle(upload_folder, dataset_slug, version_notes):
    """Upload the updated dataset to Kaggle without using the proxy."""
    # Temporarily remove proxy settings for Kaggle upload
    original_http_proxy = os.environ.pop("HTTP_PROXY", None)
    original_https_proxy = os.environ.pop("HTTPS_PROXY", None)
    try:
        api = KaggleApi()
        api.authenticate()
        api.dataset_create_version(
            folder=upload_folder,
            version_notes=version_notes,
            dir_mode=True
        )
        print("Dataset updated on Kaggle.")
    finally:
        # Restore proxy settings after upload
        if original_http_proxy:
            os.environ["HTTP_PROXY"] = original_http_proxy
        if original_https_proxy:
            os.environ["HTTPS_PROXY"] = original_https_proxy

def main():
    # Solana dataset slug - you'll need to create this on Kaggle first
    dataset_slug = "novandraanugrah/solana-price-data-binance-api-2020now"
    
    # Create directories if they don't exist
    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(NEW_DATA_FOLDER, exist_ok=True)
    os.makedirs(MERGED_FOLDER, exist_ok=True)

    # Step 1: Clean folders (do not remove metadata until after successful upload)
    clean_folder(DATA_FOLDER)
    clean_folder(NEW_DATA_FOLDER)
    clean_folder(MERGED_FOLDER)

    # Step 2: Download Kaggle dataset and metadata into DATA_FOLDER
    download_kaggle_dataset(dataset_slug, DATA_FOLDER)

    # Step 3: Fetch new data for all timeframes
    # Start from 2025-01-01 to get only the latest data for updates
    start_date = "2025-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    timeframes = {
        "15m": Client.KLINE_INTERVAL_15MINUTE,
        "1h": Client.KLINE_INTERVAL_1HOUR,
        "4h": Client.KLINE_INTERVAL_4HOUR,
        "1d": Client.KLINE_INTERVAL_1DAY
    }

    for tf_name, tf_interval in timeframes.items():
        output_file = os.path.join(NEW_DATA_FOLDER, f"{tf_name}.csv")
        fetch_binance_data("SOLUSDT", tf_interval, start_date, end_date, output_file)

    # Step 4: Merge new data with old datasets and save the merged files in MERGED_FOLDER
    current_year = datetime.now().year
    for tf_name, _ in timeframes.items():
        # Solana data files follow the pattern sol_{timeframe}_data_2020_to_{current_year}.csv
        old_file = os.path.join(DATA_FOLDER, f"sol_{tf_name}_data_2020_to_{current_year}.csv")
        new_file = os.path.join(NEW_DATA_FOLDER, f"{tf_name}.csv")
        merged_file = os.path.join(MERGED_FOLDER, f"sol_{tf_name}_data_2020_to_{current_year}.csv")
        merge_datasets(old_file, new_file, merged_file)
    
    # Copy metadata file from DATA_FOLDER to MERGED_FOLDER so that Kaggle API finds it
    copy_metadata(DATA_FOLDER, MERGED_FOLDER)

    # Step 5: Upload updated datasets from MERGED_FOLDER with a retry loop until successful
    current_date = datetime.now().strftime("%B, %d %Y")
    upload_successful = False
    while not upload_successful:
        try:
            upload_to_kaggle(MERGED_FOLDER, dataset_slug, f"Update {current_date}")
            upload_successful = True
        except Exception as e:
            print(f"Upload failed: {e}. Retrying in 60 seconds...")
            time.sleep(60)

    # Step 6: Once upload is successful, clean all folders
    clean_folder(DATA_FOLDER)
    clean_folder(NEW_DATA_FOLDER)
    clean_folder(MERGED_FOLDER)

if __name__ == "__main__":
    max_attempts = 10  # Maximum number of global attempts
    attempt = 0
    while attempt < max_attempts:
        try:
            main()
            break  # Exit loop if main() succeeds
        except Exception as e:
            attempt += 1
            print(f"Global attempt {attempt}/{max_attempts} failed: {e}")
            print("Retrying in 60 seconds...")
            time.sleep(60)
    else:
        print("Max attempts reached. Exiting.")
        sys.exit(1) 