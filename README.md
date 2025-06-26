# Solana Dataset Kaggle Auto-Updater

An automated system to fetch Solana historical price data from Binance API and maintain an up-to-date dataset on Kaggle.

## 🚀 Features

- **Complete Historical Coverage**: Fetches Solana data from August 11, 2020 (earliest available) to present
- **Multiple Timeframes**: 15-minute, 1-hour, 4-hour, and daily intervals
- **Automated Updates**: Scheduled updates to keep Kaggle dataset current
- **Error Handling**: Robust retry mechanisms and proxy support
- **Data Validation**: Ensures data integrity and removes duplicates

## 📊 Dataset Information

- **Start Date**: August 11, 2020 (SOL/USDT trading start on Binance)
- **Symbol**: SOLUSDT (Solana vs US Dollar Tether)
- **Data Source**: Binance API
- **Update Frequency**: Daily automated updates
- **Kaggle Dataset**: [Solana Price Data Binance API (2020–Now)](https://kaggle.com/datasets/novandraanugrah/solana-price-data-binance-api-2020now)

## 🔧 Installation

### Prerequisites

- Python 3.8+
- Poetry (for dependency management)
- Binance API credentials
- Kaggle API credentials

### Setup

1. **Clone the repository**:

      ```bash
      git clone <repository-url>
      cd sol-dataset-kaggle-updater
      ```

2. **Install dependencies**:

      ```bash
      poetry install
      ```

3. **Environment Variables**:
   Create a `.env` file in the project root:
      ```
      BINANCE_API_KEY=your_binance_api_key
      BINANCE_API_SECRET=your_binance_secret_key
      KAGGLE_USERNAME=your_kaggle_username
      KAGGLE_KEY=your_kaggle_api_key
      ```

## 📁 Project Structure

```
sol-dataset-kaggle-updater/
├── solana_dataset_kaggle_auto_updater/
│   ├── data/                    # Downloaded Kaggle datasets
│   ├── new_data/               # Newly fetched data
│   ├── merged_data/            # Merged datasets for upload
│   └── kaggle_update_solana.py # Main updater script
├── solana_full_data/           # Full historical data
├── fetch_full_sol_data.py      # Complete historical data fetcher
├── pyproject.toml              # Poetry configuration
└── README.md                   # This file
```

## 🎯 Usage

### Fetch Complete Historical Data

To download all available Solana historical data:

```bash
poetry run python fetch_full_sol_data.py
```

This creates files in `solana_full_data/`:

- `sol_15m_data_2020_to_2025.csv`
- `sol_1h_data_2020_to_2025.csv`
- `sol_4h_data_2020_to_2025.csv`
- `sol_1d_data_2020_to_2025.csv`

### Update Kaggle Dataset

To run the automated updater:

```bash
poetry run python solana_dataset_kaggle_auto_updater/kaggle_update_solana.py
```

Or use the Poetry script:

```bash
poetry run update-solana
```

## 📈 Data Schema

Each CSV file contains the following columns:

| Column                       | Description                      |
| ---------------------------- | -------------------------------- |
| Open time                    | Opening time of the candle (UTC) |
| Open                         | Opening price                    |
| High                         | Highest price during the period  |
| Low                          | Lowest price during the period   |
| Close                        | Closing price                    |
| Volume                       | Volume traded in SOL             |
| Close time                   | Closing time of the candle (UTC) |
| Quote asset volume           | Volume in USDT                   |
| Number of trades             | Number of trades executed        |
| Taker buy base asset volume  | Volume of SOL bought by takers   |
| Taker buy quote asset volume | Volume of USDT used by takers    |
| Ignore                       | Unused field                     |

## 🔄 Automation

The system is designed to run automatically via:

- **GitHub Actions**: Scheduled workflows for continuous updates
- **Cron Jobs**: Server-based scheduling
- **Manual Execution**: On-demand updates

## 🛠️ Technical Details

### API Rate Limits

- Binance API: Respects rate limits with built-in delays
- Retry mechanisms with exponential backoff
- Proxy support for restricted regions

### Data Processing

1. **Download**: Fetches existing dataset from Kaggle
2. **Fetch**: Gets new data from Binance API
3. **Merge**: Combines datasets, removes duplicates
4. **Validate**: Ensures data integrity
5. **Upload**: Updates Kaggle dataset

### Error Handling

- Connection retry logic
- Proxy failover support
- Data validation checks
- Comprehensive logging

## 🌟 Solana vs Other Cryptocurrencies

**Historical Coverage Comparison**:

- **Bitcoin**: ~7.9 years (since August 2017)
- **Ethereum**: ~7.9 years (since August 2017)
- **Solana**: ~4.9 years (since August 2020)

**Why Solana has less history**:

- Solana mainnet launched March 16, 2020
- Trading started August 11, 2020 on Binance
- This represents nearly complete trading history!

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- [Bitcoin Dataset Kaggle Auto-Updater](../bitcoin-dataset-kaggle-auto-updater/)
- [Ethereum Dataset Kaggle Auto-Updater](../eth-dataset-kaggle-updater/)

## 📞 Support

For issues and questions:

- Open an issue on GitHub
- Check the existing documentation
- Review the logs for error details

---

**Note**: This project focuses on SOL/USDT pair for consistency with other cryptocurrency datasets. For earlier data (starting April 10, 2020), SOL/BTC pairs are available but not included in this dataset for simplicity.
