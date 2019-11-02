# from database import db
import yaml
# from sqlalchemy import _or
import pandas as pd
import pandas_datareader as pdr
import pandas_datareader.data as web
from pandas_datareader.stooq import StooqDailyReader

class IndexList:
    """ Class to manage lists of indexes

        Parameter:
            yaml_file (string): yaml file path containing indexes
            start_date (datetime.date): start_date to query
            end_date (datetime.date): end_date to query

    """

    def __init__(self, yaml_file, start_date, end_date):
        # csv to store stock data (optional)
        self.csv_file = "stock_data.csv"

        #
        self.start_date = start_date
        self.end_date = end_date

        # Index data list
        self.indices = []

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
                    "csv": read from default csv file
                    "web": read from web sources (default)
                    "db":  read from default database

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
                    new_index.define_quotations(stooq_data)
                    self.indices.append(new_index)
                else:
                    print("Read error.")
        elif source == "csv":
            # read from default csv file
            print(1)

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
            session=None
        ).read()


class Index:
    """ Class to store temporal index data """
    def __init__(self, name, symbol, start_date, last_date):
        self.name = name
        self.symbol = symbol
        self.start_date = start_date
        self.last_date = last_date
        self.quotation_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

    def define_quotations(self, quotations):
        self.quotation_df = quotations

    def __str__(self):
        print("")
        print("-----" + self.name + "-----")
        print("from: %s to: %s" %  (self.start_date, self.last_date))
        print(self.quotation_df)
        print("")
