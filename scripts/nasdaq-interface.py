#Imports
import json
from selenium import webdriver
from bs4 import BeautifulSoup

# Helper functions
# Download webpage body
def get_website(url: str, driver_path: str) -> json:
    #Load Chrome Driver into Selenium
    driver = webdriver.Chrome(driver_path)
    
    # Download Website Source
    driver.get(url)
    html_source = driver.find_element_by_tag_name('body')

    # Soupify html source
    soup = BeautifulSoup(html_source.text, 'html.parser')

    # Close Driver and convert to soup
    driver.close()
    data = json.loads(str(soup))
    
    return data
      
# Extract Stock Tickers
def get_tickers(data: json) -> list:
    tickers = [x['symbol'] for x in data['data']['table']['rows']]
    return tickers

def main():
    
    # API Endpoints for NYSE and NASDAQ mega, large, and mid size companies.
    # Possble choices are mega|large|mid|small|micro|nano
    nasdaq = "https://api.nasdaq.com/api/screener/stocks?exchange=NASDAQ&marketcap=mega|large|mid&tableonly=true&limit=3000"
    nyse = "https://api.nasdaq.com/api/screener/stocks?exchange=NYSE&marketcap=mega|large|mid&tableonly=true&limit=3000"
    
    data = get_website(nasdaq, './\chromedriver_win32/chromedriver')
    nasdaq_tickers = get_tickers(data)

    data = get_website(nyse, './\chromedriver_win32/chromedriver')
    nyse_tickers = get_tickers(data)
    
    return nasdaq_tickers, nyse_tickers

if __name__ == "__main__":
    main()