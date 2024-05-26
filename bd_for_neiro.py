import yfinance as yf
import pandas as pd
import schedule
from datetime import datetime
from predict_script import predict_crypto
from config import SHORT_ACTIONS
import json


def get_top_20_stocks():
    start_date='2010-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    top_20_tickers = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'TSLA', 'BRK-A', 'BRK-B',
                      'V', 'JPM', 'NVDA', 'MA', 'PG', 'DIS', 'UNH', 'BAC', 'HD', 'PYPL']
    crypto_tickers = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'AVAX-USD', 'BASIC-USD',
                      'LINK-USD', 'DAI-USD', 'DEFI-USD', 'MATIC-USD', 'SOL-USD', 'XRP-USD', 'ADA-USD']

    all_data = pd.DataFrame()
    result = {}
    for ticker in top_20_tickers + crypto_tickers:
        data = yf.download(ticker, start=start_date, end=end_date)
        result[ticker[:-4] if 'USD' in ticker else SHORT_ACTIONS[ticker]] = predict_crypto(data)
    with open("predict.json", "w") as file:
        json.dump(result, file)
