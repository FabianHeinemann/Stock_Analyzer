import yaml
import sqlalchemy as db
import pandas as pd
import pandas_datareader.data as web
from pandas import DataFrame
from pandas_datareader.stooq import StooqDailyReader
import yfinance as yf
import requests
import datetime
import numpy as np
from database import db_session
from model import DataVendor, Security, Exchange, Quotation


class DataController:
    """ Class to control data import from different
    files or websites"""

    def __init__(self):
        pass

    def add_data_vendor(self, name=None, website=None):
        date = datetime.datetime.now()
        datavendor = DataVendor(name=name, website=website, created_date=date,
                                last_updated=date)
        db_session.add(datavendor)
        db_session.commit()

    def add_security(self, name, type, symbol):
        date = datetime.datetime.now()
        security = Security(name=name, type=type, symbol=symbol,
                            created_date=date, last_updated=date)
        db_session.add(security)
        db_session.commit()

    def add_security_from_csv(self, csvfile):
        # read from csv file
        print("Read from csv: %s" % (csvfile))
        securities = pd.read_csv(csvfile, sep=';')
        print("Processing entries...")
        for row in securities.itertuples():
            print(row.Name + " " + row.Type + " " + row.Symbol)
            self.add_security(row.Name, row.Type, row.Symbol)

    def addQuotation(self, date, open, high, low, close, adj_close, volume,
                     created_date, last_updated, datavendor, security):

        db_session.add(Quotation(date=date, open=open, high=high, low=low,
                       close=close, adj_close=adj_close, volume=volume,
                       created_date=created_date,
                       last_updated=last_updated,
                       data_vendor_id=datavendor.id,
                       security_id=security.id))

    def update_quotation(self, symbol, datavendor):
        start_date = datetime.date(2000, 1, 1)
        end_date = datetime.datetime.now()
        if datavendor == "Yahoo":
            print(symbol)
            dv = db_session.query(DataVendor).filter_by(name=datavendor).one()
            sec = db_session.query(Security).filter_by(symbol=symbol).one()
            yf.pdr_override()
            yahoo_data = web.get_data_yahoo(symbol, start=start_date,
                                            end=end_date)
            if not yahoo_data.empty:
                # Create new index object
                print("begin quotes")
                for index, quotation in yahoo_data.iterrows():
                    print(quotation)
                    self.addQuotation(date=index,
                                       open=quotation["Open"],
                                       high=quotation["High"],
                                       low=quotation["Low"],
                                       close=quotation["Close"],
                                       adj_close=quotation["Adj Close"],
                                       volume=quotation["Volume"],
                                       created_date=end_date,
                                       last_updated=end_date,
                                       datavendor=dv,
                                       security=sec)
                db_session.commit()
            else:
                print("Read error.")


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




class IndexList:
    """ Class to manage lists of indexes

    Parameters:
        start_date (datetime.date): start_date to query
        end_date (datetime.date): end_date to query
        proxies:  proxy dict. Default: {} (no proxy)
        yaml_file(string, Default: stocks.yaml): yaml containing dict of indexes and names.

    """

    def __init__(self, start_date, end_date, proxies=None,
                 yaml_file="indices_yahoo.yaml"):
        # csv file name to store stock data (optional)
        self.csv_file = "stock_data.csv"

        # db connect string to store stock data (optional)
        #self.db_connect_string = 'sqlite:///stock_data.db'

        if proxies is None:
            proxies = {}

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
        """ Reads index list from yaml and returns result as dictionary.

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
                    "yahoo": read from yahoo

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
                    new_index = Index(self.index_dict.get(symbol),
                                      symbol, stooq_data.index[-1],
                                      stooq_data.index[0])
                    # Add dataframe with time series data
                    new_index.set_quotations(stooq_data)
                    self.indices.append(new_index)
                else:
                    print("Read error.")
        elif source == "yahoo":
            for symbol in self.index_dict:
                print(symbol)
                yf.pdr_override()
                yahoo_data = web.get_data_yahoo(symbol, start=self.start_date,
                                                end=self.end_date)
                if not yahoo_data.empty:
                    # Create new index object
                    index = Index(name=self.index_dict.get(symbol),
                                  symbol=symbol,
                                  start_date=self.start_date,
                                  end_date=self.end_date)
                    # Add dataframe with time series data
                    db_session.add(index)
                    db_session.commit()
                    delta = datetime.timedelta(days=1)
                    current_date = self.start_date
                    print("begin quotes")
                    for i, d in yahoo_data.iterrows():
                        db_session.add(Quotation(date=i,
                                                 open=float(d['Open']),
                                                 high=float(d['High']),
                                                 low=float(d['Low']),
                                                 close=float(d['Close']),
                                                 volume=float(d['Volume']),
                                                 index=index))
                    db_session.commit()
                    self.indices.append(index)
                else:
                    print("Read error.")
        elif source == "csv":
            # read from csv file
            print("Read from csv: %s" % (self.csv_file))

            # Read csv
            indexes_dataframe = pd.read_csv(self.csv_file, parse_dates=["Date"])

            # Update indexes from dataframe
            self.update_indexes_from_dataframe(indexes_dataframe)

        elif source == "db":
            # read from database
            print("Read from databse: %s" % (self.db_connect_string))

            indexes_dataframe = pd.read_sql_table('Indexes', self.db_connect_string)  # type: DataFrame

            # Update indexes from dataframe
            if not indexes_dataframe.empty:
                self.update_indexes_from_dataframe(indexes_dataframe)

        elif source == "test":
            # generate empty test data
            for symbol in self.index_dict:
                index = Index(name=self.index_dict.get(symbol), symbol=symbol,
                              start_date=self.start_date,
                              end_date=self.end_date)
                db_session.add(index)
                db_session.commit()
                delta = datetime.timedelta(days=1)
                current_date = self.start_date
                while current_date <= self.end_date:
                    db_session.add(Quotation(date=current_date, close=np.random.rand(1)[0], index=index))
                    current_date += delta
                    print(current_date)
                db_session.commit()
                self.indices.append(index)

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

            # Create a dataframe containing all data
            indexes_dataframe = pd.DataFrame()
            for i in self.list_indices():
                indexes_dataframe = indexes_dataframe.append(i.quotation_df, ignore_index=True)

            # Save to disk
            indexes_dataframe.to_csv(self.csv_file, index=False)

        elif target == "db":
            # Serialize to database

            # Create a dataframe containing all data
            indexes_dataframe = pd.DataFrame()
            for i in self.list_indices():
                indexes_dataframe = indexes_dataframe.append(i.quotation_df, ignore_index=True)

            # Create database engine object
            db_engine = db.create_engine(self.db_connect_string)

            # Save to database
            # To do: Add unique keys (Id-timestamp)
            indexes_dataframe.to_sql("Indexes", con=db_engine, if_exists="replace")

    def update_indexes_from_dataframe(self, indexes_dataframe):
        """ Update indexes dict and indexes from dataframe
        Parameter:
            indexes_dataframe (Pandas Dataframe): Contains index data
        Returns:
            (nothing)
        """
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


