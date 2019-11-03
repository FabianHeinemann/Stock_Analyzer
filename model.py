# from database import db
import yaml
# from sqlalchemy import _or
import pandas as pd
import pandas_datareader as pdr
import pandas_datareader.data as web
from pandas_datareader.stooq import StooqDailyReader
import requests
import datetime
import numpy as np

class IndexList:
    """ Class to manage lists of indexes

        Parameters:
            yaml_file (string): yaml file path containing indexes
            start_date (datetime.date): start_date to query
            end_date (datetime.date): end_date to query
            proxies:  proxy dict. Default: {} (no proxy)

    """

    def __init__(self, yaml_file, start_date, end_date, proxies = {}):
        # csv to store stock data (optional)
        self.csv_file = "stock_data.csv"

        #
        self.start_date = start_date
        self.end_date = end_date

        # Index data list
        self.indices = []

        self.session = None
        if (proxies):
            # Create the session and set the proxies.
            self.session = requests.Session()
            self.session.proxies.update(proxies)

        # Read indexes from yaml
        self.index_dict = {}
        with open(yaml_file, 'r') as yaml_file:
            try:
                self.index_dict = yaml.safe_load(yaml_file)["indexes"]
            except yaml.YAMLError as exc:
                print(exc)

    def list_indices(self):
        return self.indices

    def initialize_indexes(self, source="web"):
        """ Starts a full update of all indexes from the sources
            Times are defined by self.start_date and self.end_date
        Parameter:
            source (string): Selects source
                    "csv": read from csv file
                    "web": read from web sources (default)
                    "db":  read from database
                    "test": generate empty test data

        Returns:
            (nothing):    self.indexes is populated
       """
        if source == "web":
            # Read from web
            for symbol in self.index_dict:
                print(symbol)
                stooq_data = self.get_stooq_data(symbol)
                if not(stooq_data.empty):
                    new_index = Index(self.index_dict.get(symbol), symbol, stooq_data.index[-1], stooq_data.index[0])
                    new_index.set_quotations(stooq_data)
                    self.indices.append(new_index)
                else:
                    print("Read error.")
        elif source == "csv":
            # read from csv file
            # tbd
            pass
        elif source == "db":
            # read from database
            # tbd
            pass
        elif source == "test":
            # generate empty test data
            for symbol in self.index_dict:
                print(symbol)

                new_index = Index(self.index_dict.get(symbol), symbol, self.start_date, self.end_date)

                # Create test dataframe
                test_data = pd.DataFrame()
                delta = datetime.timedelta(days=1)
                current_date = self.start_date
                while current_date <= self.end_date:
                    current_date += delta
                    test_data = test_data.append({"Date": current_date, "Quotation": np.random.rand(1)[0], "Id" : symbol, "Name" : self.index_dict.get(symbol)}, ignore_index=True)

                new_index.set_quotations(test_data)
                self.indices.append(new_index)



    def get_stooq_data(self, symbol):
        """ Returns stooq temporal stock data for a given symbol
            https://stooq.pl/
            Times are defined by self.start_date and self.end_date

        Parameters:
            symbol (str): Symbol (e.g. "^SPX" for "S&P 500 - U.S.")

        Returns:
            Pandas Dataframe: Table of results
       """
        return StooqDailyReader(
            symbols=symbol,
            start=self.start_date,
            end=self.end_date,
            chunksize=25,
            retry_count=3,
            pause=0.1,
            session=self.session
        ).read()

class Index:
    """ Class to store index data
        Parameters:
            name (string): name of index
            symbol (string): unique symbol
            start_date (datetime.date): start date of index
            last_date (datetime.date): last available date of index
       """
    def __init__(self, name, symbol, start_date, last_date):
        self.name = name
        self.symbol = symbol
        self.start_date = start_date
        self.last_date = last_date
        self.quotation_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

    def set_quotations(self, quotations):
        """ Set quotation data
            Parameter:
                quotations (pandas dataframe): dataframe containing quotations data
           """
        self.quotation_df = quotations

    def __str__(self):
        return("----- + %s + -----\nfrom: %s to: %s" %  (self.name, self.start_date, self.last_date))