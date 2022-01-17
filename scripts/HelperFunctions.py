import os
from datetime import datetime
import shutil
import time
import glob
import smtplib
import ssl

import yfinance as yf
import pandas as pd

def initialize_folders(file_path: str) -> None:
    # Delete and create file path for storing stock information
    
    if os.path.exists(file_path):
        shutil.rmtree(file_path)
        os.makedirs(file_path)
    else:
        os.makedirs(file_path)
    return None

def download_stock_data (file_path: str, tickers: pd.DataFrame, sleep_time: float = 0.0) -> None:
    # Downloads stock data from Yahoo Finance APIs
    
    # Holds the amount of API calls we executed
    api_calls = 0

    # This while loop is reponsible for storing the historical data for each ticker in our list. Note that yahoo finance sometimes incurs json.decode errors and because of this we are sleeping for 2
    # seconds after each iteration, also if a call fails we are going to try to execute it again.
    # Used to make sure we don't waste too many API calls on one Stock ticker that could be having issues
    api_failures = 0
    failed_imports = 0

    # Used to iterate through our list of tickers
    start_time = datetime.now()
    print("[-] Started at " + str(start_time))
    i=0
    while (i < len(tickers)) and (api_calls < 3000):
        try:
            stock = tickers[i]  # Gets the current stock ticker
            temp = yf.Ticker(str(stock))
            historical_data = temp.history(period="max")  # Tells yfinance what kind of data we want about this stock (In this example, all of the historical data)
            historical_data.to_csv(file_path+stock+".csv")  # Saves the historical data in csv format for further processing later
            time.sleep(sleep_time)  # Pauses the loop for one seconds so we don't cause issues with Yahoo Finance's backend operations
            api_calls += 1 
            api_failures = 0
            i += 1  # Iteration to the next ticker
        except ValueError:
            print("Yahoo Finance Backend Error, Attempting to Fix")  # An error occured on Yahoo Finance's backend. We will attempt to retreive the data again
            if api_failures > 5:  # Move on to the next ticker if the current ticker fails more than 5 times
                i+=1
                failed_imports += 1
            api_calls += 1
            api_failures += 1
    end_time = datetime.now()
    print("[+] Completed at " + str(end_time))
    print("[*] Total Time: " + str(end_time - start_time))
    print("The amount of stocks we successfully imported: " + str(i - failed_imports))
    
    return None

def calculate_obv (file_path: str, history: int = 20) -> None:
    list_files = (glob.glob(file_path + "*.csv"))
    new_data = [] #  This will be a 2D array to hold our stock name and OBV score
    interval = 0  # Used for iteration
    while interval < len(list_files):
        file = list_files[interval]
        data = pd.read_csv(file).tail(history)
        if (len(data) < history):
            os.remove(file)
        interval += 1
    
    # OBV Analysis
    list_files = (glob.glob(file_path + "*.csv")) # Creates a list of all csv filenames in the stocks folder
    new_data = [] #  This will be a 2D array to hold our stock name and OBV score
    interval = 0  # Used for iteration
    while interval < len(list_files):
        file = list_files[interval]
        data = pd.read_csv(file).tail(20)  # Gets the last 20 days of trading for the current stock in iteration
        #print(data.iloc[0,0], data.iloc[-1,0])
        #break
        pos_move = []  # List of days that the stock price increased
        neg_move = []  # List of days that the stock price increased
        OBV_Value = 0  # Sets the initial OBV_Value to zero
        count = 0
        while (count < history):
            if data.iloc[count,1] < data.iloc[count,4]:  # True if the stock increased in price
                pos_move.append(count)  # Add the day to the pos_move list
            elif data.iloc[count,1] > data.iloc[count,4]:  # True if the stock decreased in price
                neg_move.append(count)  # Add the day to the neg_move list
            count += 1
        count2 = 0
        for i in pos_move:  # Adds the volumes of positive days to OBV_Value, divide by opening price to normalize across all stocks
            OBV_Value = round(OBV_Value + (data.iloc[i,5]/data.iloc[i,1]))
        for i in neg_move:  # Subtracts the volumes of negative days from OBV_Value, divide by opening price to normalize across all stocks
            OBV_Value = round(OBV_Value - (data.iloc[i,5]/data.iloc[i,1]))
        Stock_Name = ((os.path.basename(list_files[interval])).split(".csv")[0])  # Get the name of the current stock we are analyzing
        new_data.append([Stock_Name, OBV_Value])  # Add the stock name and OBV value to the new_data list
        interval += 1



    df = pd.DataFrame(new_data, columns = ['Stock', 'OBV_Value'])  # Creates a new dataframe from the new_data list
    df["Stocks_Ranked"] = df["OBV_Value"].rank(ascending = False)  # Rank the stocks by their OBV_Values
    df.sort_values("OBV_Value", inplace = True, ascending = False)  # Sort the ranked stocks
    df.to_csv("./OBV_Ranked.csv", index = False)  # Save the dataframe to a csv without the index column
    # OBV_Ranked.csv now contains the ranked stocks that we want recalculate daily and receive in a digestable format.
    
def email_results (top10: pd.DataFrame, bottom10: pd.DataFrame, 
                   email_address: str, password: str, 
                   port: int = 465) -> None:
    # This is where we write the body of our email. Add the top 10 and bottom 10 dataframes to include the results of your analysis
    Body_of_Email = """
    Subject: Daily Stock Report - EXPANDED
    
    Your highest ranked OBV stocks of the day:
    """ + top10.to_string(index=False) + """\
    
    
    Your lowest ranked OBV stocks of the day:
    """ + bottom10.to_string(index=False) + """
    
    
    Sincerely,
    Your Computer"""

    context = ssl.create_default_context()
    port = 465  # If you are not using a gmail account, you will need to look up the port for your specific email host
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email_address, password)  #  This statement is of the form: server.login(<Your email>, "Your email password")
        server.sendmail(email_address, email_address, Body_of_Email)  # This statement is of the form: server.sendmail(<Your email>, <Email receiving message>, Body_of_Email)
        
    return None