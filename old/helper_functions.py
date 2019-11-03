import pandas as pd
import json
import urllib
import requests
from bs4 import BeautifulSoup

def get_stock_data(data_type, name):
    """ This function retireves stock data from www.wallstreet-online.de and stores the result in a dataframe
    
    Arguments: 
        data_type (string): type of data "stock" or "index"
        name (string): name of data, e.g. "bitcoin-group", "volkswagen", "dowjones"
          
    Return:
        Pandas dataframe: Columns "Day_cts", "Dates", "Start", "Max", "Min", "End", "volume" and "t_in_sec". Will return empty dataframe in case of error
    """

    # Call webpage with chart data 
    if data_type == "stock":
        quote_page = "https://www.wallstreet-online.de/aktien/"+name+"-aktie/chart#t:max||s:lines||a:abs||v:day||ads:null"
    else:
        quote_page = "https://www.wallstreet-online.de/indizes/"+name+"/chart#t:max||s:lines||a:abs||v:day||ads:null"
    
    # Load page in variable and analyze
    try:
        page = urllib.request.urlopen(quote_page)
        pass
    except urllib.error.URLError:
        # Something went wrong
        return pd.DataFrame()
        
    soup = BeautifulSoup(page, "html.parser") 
    inst_id = soup.find("input", attrs={"name": "inst_id"})["value"]
    market_id = soup.find("input", attrs={"class": "marketSelect"})["value"]
    
    # Get JSON file with chart data
    url = "https://www.wallstreet-online.de/_rpc/json/instrument/chartdata/loadRawData?q%5BinstId%5D="+inst_id+"&q%5BmarketId%5D="+market_id+"&q%5Bmode%5D=hist"
    resp = requests.get(url=url)
    data = json.loads(resp.text)
        
    # Store the stock data in Pandas Dataframe
    end = data["markets"][market_id]["lastUpdate"][0:10]
    day_cts = len(data["data"])
    dates = pd.date_range(end=end, periods=day_cts, freq="B")
    
    # Adjust for holidays
    if data["data"][-1][-1] == None:
        end = dates[-1]+1
        
    dates = pd.date_range(end=end, periods=day_cts, freq="B")
    columns = ["day_cts", "opening", "max", "min", "end", "volume", "t_in_sec"]
    stock_data = pd.DataFrame(data["data"], columns=columns)
    stock_data.insert(1,"date",dates)
    stock_data["_id"] = stock_data["date"].apply(lambda x: name + " " + str(x.strftime("%Y-%m-%d")))
    stock_data["name"] = name
    
    return stock_data