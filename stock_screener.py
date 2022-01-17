# imports
import shutil
import os 
import time 
import glob
import smtplib
import ssl

from datetime import datetime
import yfinance as yf
import pandas as pd

from scripts import NasdaqInterface, HelperFunctions

# Constants
# NASDAQ API endpoints
NASDAQ = "https://api.nasdaq.com/api/screener/stocks?exchange=NASDAQ&marketcap=mega|large|mid&tableonly=true&limit=3000"
NYSE = "https://api.nasdaq.com/api/screener/stocks?exchange=NYSE&marketcap=mega|large|mid&tableonly=true&limit=3000"

# Save locations
FILE_PATH = r'./Stock_Report/Stocks/'

# Read NASDAQ Stocks
data = NasdaqInterface.get_website(NASDAQ, './drivers/chromedriver_win32/chromedriver')
nasdaq_tickers = NasdaqInterface.get_tickers(data)

# Read NYSE Stocks
data = NasdaqInterface.get_website(NYSE, './drivers/chromedriver_win32/chromedriver')
nyse_tickers = NasdaqInterface.get_tickers(data)
tickers = nasdaq_tickers + nyse_tickers

print("The amount of stocks chosen to observe: " + str(len(tickers)))

# Save tickers for laters use
pd.DataFrame(nasdaq_tickers).to_csv("nasdaq.csv", index=False)
pd.DataFrame(nyse_tickers).to_csv("nyse.csv", index=False)

# Ceate file structure
HelperFunctions.initialize_folders(FILE_PATH)

# Download stock data
HelperFunctions.download_stock_data(FILE_PATH, tickers)

# HelperFunctionsculate On-Balance Volume and get Top 10 and Bottom 10 Stocks
HelperFunctions.calculate_obv(FILE_PATH)

Analysis = pd.read_csv("./OBV_Ranked.csv")  # Read in the ranked stocks

top10 = Analysis.head(10)  # I want to see the 10 stocks in my analysis with the highest OBV values
bottom10 = Analysis.tail(10)  # I also want to see the 10 stocks in my analysis with the lowest OBV values

print("Printing Top 10\n")
print(top10)
print("\nPrinting Bottom 10\n")
print(bottom10)