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
        start_date (datetime.date): start_date to query
        end_date (datetime.date): end_date to query
        proxies:  proxy dict. Default: {} (no proxy)
        yaml_file(string, Default: stocks.yaml): yaml containing dict of indexes and names.

    """

    def __init__(self, start_date, end_date, proxies=None, yaml_file="stocks.yaml"):
        # csv file name to store stock data (optional)
        if proxies is None:
            proxies = {}
        self.csv_file = "stock_data.csv"

        # yaml_file to read indexes dict from
        self.yaml_file = yaml_file

        # Read index_dict from yaml
        self.index_dict = {}
        if self.yaml_file:
            self.index_dict = self.read_index_list_from_yaml()

        #
        self.start_date = start_date
        self.end_date = end_date

        # Index data list
        self.indices = []

        self.session = None
        if proxies:
            # Create the session and set the proxies.
            self.session = requests.Session()
            self.session.proxies.update(proxies)

    def list_indices(self):
        return self.indices

    def read_index_list_from_yaml(self):
        """ Reads index list from yaml. Will populate self.index list.

        returns:
            index_dict: Dictionary of index_id - index_name pairs

        """
        # Read indexes from yaml
        index_dict = {}
        with open(self.yaml_file, 'r') as f:
            try:
                index_dict = yaml.safe_load(f)["indexes"]
            except yaml.YAMLError as exc:
                print(exc)

        return index_dict

    def initialize_indexes(self, source="web"):
        """ Performs a full update of all indexes from the sources
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
            print("Read from web")
            for symbol in self.index_dict:
                print(symbol)
                stooq_data = self.get_stooq_data(symbol)
                if not stooq_data.empty:
                    # Create new index object
                    new_index = Index(self.index_dict.get(symbol), symbol, stooq_data.index[-1], stooq_data.index[0])
                    # Add dataframe with time series data
                    new_index.set_quotations(stooq_data)
                    self.indices.append(new_index)
                else:
                    print("Read error.")
        elif source == "csv":
            # read from csv file
            print("Read from csv: %s" % (self.csv_file))

            # Read csv
            indexes_dataframe = pd.read_csv(self.csv_file, parse_dates=["Date"])

            # Create index dict and index object from data in csv
            self.index_dict = {}
            for name in indexes_dataframe["Name"].unique():
                symbol = indexes_dataframe[indexes_dataframe["Name"] == name]["Symbol"].unique()[0]
                self.index_dict[symbol] = name

                start_time = min(indexes_dataframe[indexes_dataframe["Name"] == name]["Date"])
                end_time = max(indexes_dataframe[indexes_dataframe["Name"] == name]["Date"])

                # Create new index object
                new_index = Index(name, symbol, start_time, end_time)

                # Add dataframe with time series data
                new_index.set_quotations(indexes_dataframe[indexes_dataframe["Name"] == name])
                self.indices.append(new_index)

        elif source == "db":
            # read from database
            # to do
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
                    test_data = test_data.append({"Date": current_date, "Quotation": np.random.rand(1)[0], "Symbol": symbol,
                                                  "Name": self.index_dict.get(symbol)}, ignore_index=True)
                    current_date += delta

                new_index.set_quotations(test_data)
                self.indices.append(new_index)

    def serialize_indexes(self, target="csv"):
        """ Serializes data to target data store
        Parameter:
            target (string): Selects data store
                    "csv": write to csv file (default)
                    "db":  write to database
        Returns:
            (nothing)
        """
        if target == "csv":
            # Serialize to csv

            # Create a dataframe
            indexes_dataframe = pd.DataFrame()
            for i in self.list_indices():
                indexes_dataframe = indexes_dataframe.append(i.quotation_df, ignore_index=True)

            # Save to disk
            indexes_dataframe.to_csv(self.csv_file, index=False)

        elif target == "db":
            # Serialize to database
            pass

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
        """ String serialization method """
        return "----- + %s + -----\nfrom: %s to: %s" % (self.name, self.start_date, self.last_date)
