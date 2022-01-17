import requests
import json

import pandas as pd
from bs4 import BeautifulSoup

# Constants
URL = "https://main.d2elvpl4yb2i31.amplifyapp.com/"
NASDAQ_TICKERS = "nasdaq.csv"
NYSE_TICKERS = "nyse.csv"
OBV_RANKED = "OBV_Ranked.csv"
SAVE_FILE = "index.html"


def main():

    # Read in stock data
    nasdaq_tickers = pd.read_csv(NASDAQ_TICKERS)
    nyse_tickers = pd.read_csv(NYSE_TICKERS)
    obv_ranked = pd.read_csv(OBV_RANKED)
    ranked_stocks = obv_ranked["Stock"].head(10).tolist()

    # Prepare Stock Tickers for Update
    stock_list = []
    for s in ranked_stocks:
        if s in nyse_tickers['0'].to_list():
            stock_list.append('"NYSE:{}"'.format(s))
        else:
            stock_list.append('"NASDAQ:{}"'.format(s))

    # Get Latest Website
    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    # Gross way of doing it. Just setup a format of the string
    content_list = []
    updated_script_contents = """ {{\n  "width": "100%",\n  "height": 450,\n  "symbolsGroups": [\n    {{\n      "name": "Midas Top 5-10 Stocks",\n      "originalName": "Indices",\n      "symbols": [\n        {{\n          "name": {}\n        }},\n        {{\n          "name": {}\n        }},\n        {{\n          "name": {}\n        }},\n        {{\n          "name": {}\n        }},\n        {{\n          "name": {}\n        }},\n        {{\n          "name": {}\n        }},\n        {{\n          "name": {}\n        }},\n        {{\n          "name": {}\n        }},\n        {{\n          "name": {}\n        }},\n        {{\n          "name": {}\n        }}\n      ]\n    }}\n  ],\n  "showSymbolLogo": true,\n  "colorTheme": "dark",\n  "isTransparent": false,\n  "locale": "en"\n}} """.format(stock_list[0], stock_list[1], 
    stock_list[2], stock_list[3], stock_list[4], stock_list[5], stock_list[6], stock_list[7], stock_list[8], stock_list[9],)
    content_list.append(updated_script_contents)

    # Update Soup with new Script section
    soup.find("div", {"class": "tradingview-widget-container"}).contents[3].string = content_list[0]

    # Format Soup and save html file
    html = soup.prettify("utf-8")
    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        file.write(str(soup))
        
def __init__:
    main()