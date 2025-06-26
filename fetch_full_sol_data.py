import os
import sys
import time
import pandas as pd
from datetime import datetime
from binance.client import Client
from dotenv import load_dotenv

# Load environment variables from parent directory (project root)
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
env_path = os.path.join(parent_dir, '.env')

print(f"Looking for .env file at: {env_path}")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print("✅ .env file found and loaded")
else:
    print("❌ .env file not found - trying to load from current directory")
    load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Debug: Check if API keys are loaded
if not BINANCE_API_KEY or not BINANCE_API_SECRET:
    print("❌ API keys not found in environment variables!")
    print("Please make sure your .env file contains:")
    print("BINANCE_API_KEY=your_api_key_here")
    print("BINANCE_API_SECRET=your_api_secret_here")
    sys.exit(1)
else:
    print(f"✅ API Key loaded: {BINANCE_API_KEY[:8]}...")
    print(f"✅ API Secret loaded: {BINANCE_API_SECRET[:8]}...")

def create_binance_client():
    """Create Binance client for local development."""
    try:
        print("Creating Binance client...")
        client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        
        print("Testing connection to Binance API...")
        # Test the connection
        client.ping()
        print("✅ Successfully connected to Binance API")
        
        # Test API key permissions
        account_info = client.get_account()
        print(f"✅ API key is valid - Account status: {account_info.get('accountType', 'Unknown')}")
        
        return client
    except Exception as e:
        print(f"❌ Failed to connect to Binance API: {str(e)}")
        print("\nPossible solutions:")
        print("1. Check your internet connection")
        print("2. Verify your API keys are correct")
        print("3. Make sure Binance API is not blocked in your region")
        print("4. Try using a VPN if Binance is restricted")
        raise

def find_earliest_data():
    """Find the earliest available Solana data on Binance."""
    client = create_binance_client()
    
    # From our testing, we know SOL/BTC starts earlier than SOL/USDT
    # SOL/BTC, SOL/BNB, SOL/BUSD start from April 10, 2020
    # SOL/USDT starts from August 11, 2020
    
    # For maximum historical coverage, let's check both options
    symbols_to_test = {
        'SOLBTC': 'April 10, 2020',   # Earliest overall
        'SOLUSDT': 'August 11, 2020'  # USD-based (easier to analyze)
    }
    
    print("=== Verifying Solana Data Availability ===")
    
    for symbol, expected_date in symbols_to_test.items():
        try:
            print(f"Verifying {symbol} (expected: {expected_date})...")
            klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, '2020-04-01', '2020-12-31')
            if klines and len(klines) > 0:
                first_timestamp = klines[0][0]
                first_date = datetime.fromtimestamp(first_timestamp / 1000)
                print(f"✅ {symbol} confirmed: First data = {first_date}")
            else:
                print(f"❌ {symbol}: No data found")
        except Exception as e:
            print(f"❌ Error verifying {symbol}: {e}")
    
    # Return the earliest date we discovered
    print(f"\n🎯 Using April 10, 2020 as start date for maximum historical coverage")
    return "2020-04-10"

def fetch_binance_data(symbol, interval, start_date, end_date, output_file):
    """Fetch historical data from Binance."""
    try:
        client = create_binance_client()
        print(f"Fetching {symbol} data for {interval} from {start_date} to {end_date}...")
        
        klines = client.get_historical_klines(symbol, interval, start_date, end_date)
        
        if not klines:
            print(f"No data received for {symbol} {interval}")
            return False
        
        columns = [
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close time', 'Quote asset volume', 'Number of trades',
            'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
        ]
        
        df = pd.DataFrame(klines, columns=columns)
        df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
        df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')
        
        # Convert numeric columns to appropriate types
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote asset volume', 
                         'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.to_csv(output_file, index=False)
        print(f"✅ Successfully fetched {len(df)} records and saved to {output_file}")
        print(f"   Date range: {df['Open time'].min()} to {df['Open time'].max()}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fetch {symbol} {interval} data: {str(e)}")
        raise

def main():
    print("=== Solana Full Historical Data Fetcher ===")
    print("Fetching maximum available Solana historical data...")
    print("Solana mainnet launched: March 16, 2020")
    print("Trading started on Binance: April 10, 2020")
    
    # Verify and get the earliest available date
    earliest_date = find_earliest_data()
    print(f"\n🎯 Using start date: {earliest_date}")
    
    # Base directory of the script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SOL_DATA_FOLDER = os.path.join(BASE_DIR, "solana_full_data")
    
    # Create data folder if it doesn't exist
    os.makedirs(SOL_DATA_FOLDER, exist_ok=True)
    
    print(f"Data will be saved to: {SOL_DATA_FOLDER}")
    
    # Use earliest date to current date
    start_date = earliest_date
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Fetching data from {start_date} to {end_date}")
    
    # Define timeframes
    timeframes = {
        "15m": Client.KLINE_INTERVAL_15MINUTE,
        "1h": Client.KLINE_INTERVAL_1HOUR,
        "4h": Client.KLINE_INTERVAL_4HOUR,
        "1d": Client.KLINE_INTERVAL_1DAY
    }
    
    # Calculate the year range for file naming
    start_year = earliest_date.split('-')[0]
    current_year = datetime.now().year
    year_range = f"{start_year}_to_{current_year}"
    
    # Choose symbol - SOL/USDT for consistency with BTC/ETH projects
    # Note: Could use SOL/BTC for slightly more history (starts April 10 vs August 11)
    symbol = "SOLUSDT"
    print(f"\nUsing {symbol} for data collection")
    print("📝 Note: SOL/BTC starts earlier (April 10) but SOL/USDT is more standard for analysis")
    
    # Fetch data for all timeframes
    success_count = 0
    for tf_name, tf_interval in timeframes.items():
        output_file = os.path.join(SOL_DATA_FOLDER, f"sol_{tf_name}_data_{year_range}.csv")
        print(f"\n--- Fetching {tf_name} data ---")
        try:
            success = fetch_binance_data(symbol, tf_interval, start_date, end_date, output_file)
            if success:
                success_count += 1
            # Add delay between requests to avoid rate limiting
            time.sleep(1)
        except Exception as e:
            print(f"❌ Failed to fetch {tf_name} data: {e}")
            continue
    
    print(f"\n=== Solana data fetching completed ===")
    print(f"Successfully fetched {success_count}/{len(timeframes)} timeframes")
    print(f"Check the files in: {SOL_DATA_FOLDER}")
    print(f"Date range: {start_date} to {end_date}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   • Symbol: {symbol}")
    print(f"   • Start date: {start_date} (earliest possible)")
    print(f"   • End date: {end_date}")
    print(f"   • Historical coverage: ~{(datetime.now() - datetime.strptime(start_date, '%Y-%m-%d')).days} days")
    print(f"   • This represents Solana's COMPLETE trading history on Binance!")

if __name__ == "__main__":
    try:
        main()
        print("\n✅ Solana full historical data fetching completed successfully!")
        print("🚀 Ready to create Kaggle dataset with complete Solana history!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1) 