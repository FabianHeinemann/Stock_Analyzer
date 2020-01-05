import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import datetime
from database import db_session
from model import DataVendor, Security, Exchange, Quotation
import matplotlib.pyplot as plt
import os
from pandas.plotting import register_matplotlib_converters
from sqlalchemy import desc
from sqlalchemy.exc import SAWarning
import errno
import warnings
register_matplotlib_converters()
plt.rcParams.update({'figure.max_open_warning': 0})

# Ignore warning about decimals
# https://stackoverflow.com/questions/34674029/sqlalchemy-query-raises-unnecessary-warning-about-sqlite-and-decimal-how-to-spe
warnings.filterwarnings('ignore', r".*support Decimal objects natively", SAWarning, r'^sqlalchemy\.sql\.sqltypes$')

# Oldest date which is used to query data
DATE_ZERO = datetime.date(1970,1,1)

class DataController:
    """ Class to control data import from different
    files or websites"""

    def __init__(self):
        pass

    def add_data_vendor(self, name=None, website=None):
        """ Add security (e.g. a stock or an index) to table security """
        date = datetime.datetime.now()
        datavendor = DataVendor(name=name, website=website, created_date=date,
                                last_updated=date)
        # Only add datavendor if not an entry with than name exists
        if db_session.query(DataVendor).filter_by(name=name).first() is None:
            db_session.add(datavendor)
            db_session.commit()

    def add_security(self, name, type, symbol):
        """ Add security (e.g. a stock or an index) to table security """
        date = datetime.datetime.now()
        security = Security(name=name, type=type, symbol=symbol,
                            created_date=date, last_updated=date)

        # Only add security if not exists
        if db_session.query(Security).filter_by(symbol=symbol).first() is None:
            db_session.add(security)
            db_session.commit()

    def add_security_from_csv(self, csvfile):
        """ Read available securities from csv file

            Expected order of columns: name; type; symbol
            Example: ^DJI;Dow 30;Index

            Parameters:
                csvfile (string): Filename of csv file
            Returns:
                -
        """
        print("Read from csv: %s" % (csvfile))
        securities = pd.read_csv(csvfile, sep=';')
        print("Processing entries...")
        for row in securities.itertuples():
            print(row.Name + " " + row.Type + " " + row.Symbol)
            self.add_security(row.Name, row.Type, row.Symbol)

    def add_quotation(self, date, open, high, low, close, adj_close, volume,
                      created_date, last_updated, datavendor, security):
        """ Add quotation to the database table <quotations>.
            This table contains the time series data of security prices.

            Parameters:
                date (sqlalchemy.types.DateTime): Date of quote
                open (sqlalchemy.types.Numeric): Opening price
                high (sqlalchemy.types.Numeric): Highest price
                low (sqlalchemy.types.Numeric): Lowest price
                close (sqlalchemy.types.Numeric): Closing price
                adj_close (sqlalchemy.types.Numeric): Adjusted closing price
                volume (sqlalchemy.types.Numeric): Volume
                created_date (sqlalchemy.types.DateTime): Creation of entry
                last_updated (sqlalchemy.types.DateTime): Last update of entry
                datavendor (DataVendor): Datavendor object
                security (Security): Security object

            Returns:
                -
        """

        db_session.add(Quotation(date=date, open=open, high=high, low=low,
                       close=close, adj_close=adj_close, volume=volume,
                       created_date=created_date,
                       last_updated=last_updated,
                       data_vendor_id=datavendor.id,
                       security_id=security.id))

    def update_quotation(self, symbol, datavendor, start_date=DATE_ZERO, end_date=datetime.datetime.now()):
        """ Read quotation from datavendor and save to database table <quotations>

                Parameters:
                    symbol (string): Symbol of the security to obtain as dataframe
                                     (e.g. "^SPX" for "S&P 500 - U.S.")
                    datavendor (string): datavendor (e.g. Yahoo) to use
                    start_date (datetime): Start date of data reading and writing
                    end_date (datetime): End date of data reading and writing

                Returns:
                    stores data to database
                """
        if datavendor == "Yahoo":
            print("Current security:%s" % (symbol))
            dv = db_session.query(DataVendor).filter_by(name=datavendor).one()
            sec = db_session.query(Security).filter_by(symbol=symbol).one()
            yf.pdr_override()

            print("Read quotes from %s" % (datavendor))
            yahoo_data = web.get_data_yahoo(symbol, start=start_date,
                                            end=end_date)
            if not yahoo_data.empty:
                # Create new index object

                print("Add quotes to db from %s to %s" % (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
                for index, quotation in yahoo_data.iterrows():
                    # print(quotation)
                    self.add_quotation(date=index,
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

    def get_security_quotes_as_dataframe(self, symbol):
        """ Get a security quotes as a dataframe

        Parameters:
            symbol (string): Symbol of the security to obtain as dataframe
                             (e.g. "^SPX" for "S&P 500 - U.S.")
        Returns:
            Pandas Dataframe: Table of results (empty on error)
        """

        # Get security object
        security = db_session.query(Security).filter_by(symbol=symbol).one()

        # Return object
        security_df = pd.DataFrame()
        if security is not None:
            # Get security data as dataframe
            quotations = db_session.query(Quotation).filter_by(security_id=security.id).all()

            date_list = []
            adj_close_list = []
            volume_list = []
            for quotation in quotations:
                date_list.append(quotation.date)
                adj_close_list.append(quotation.adj_close)
                volume_list.append(quotation.volume)

            security_df = pd.DataFrame({"Date": date_list, "adj_close": adj_close_list, "Volume": volume_list})

        return security_df

    def get_latest_update(self, symbol):
        """ Get time of latest update for given security

                Parameters:
                    symbol (string): Symbol of the security to obtain as dataframe
                                     (e.g. "^SPX" for "S&P 500 - U.S.")

                Returns:
                    date of last update (datetime.date()). Will return DATE_ZERO in case of empty db.
                """

        security = db_session.query(Security).filter_by(symbol=symbol).one()
        if security is not None:
            # Get date of latest entry
            quotation = db_session.query(Quotation).filter_by(security_id=security.id).order_by(desc(Quotation.date)).first()

            if quotation is not None:
                last_update = quotation.date.date()
            else:
                last_update = DATE_ZERO

        return last_update

    def plot_security(self, symbol, savepath="./plots/"):
        """ Plot security quotes and save as png under plots

        Parameters:
            symbol (string): Symbol of the security to obtain as dataframe
                             (e.g. "^SPX" for "S&P 500 - U.S.")
            savepath (string): Path where figure will be saved

        Returns:
            Saves a figure symbol.png
        """

        # Get security name
        security = db_session.query(Security).filter_by(symbol=symbol).one()

        # Dataframe of security
        security_df = self.get_security_quotes_as_dataframe(symbol)

        # Get rolling average of security
        security_df["adj_close_100_days_average"] = security_df["adj_close"].rolling(window=100).mean()

        # Get rolling standard deviation of security using the last 15 days
        security_df["adj_close_100_days_std"] = security_df["adj_close"].rolling(window=15).std()

        # 95% confidence interval of stock, i.e. +/- 2*standard deviation (only true if chart is Gaussian distributed)
        security_df["adj_close_high"] = security_df["adj_close"].astype("float32") + 2*security_df["adj_close_100_days_std"]
        security_df["adj_close_low"] = security_df["adj_close"].astype("float32") - 2*security_df["adj_close_100_days_std"]

        if not security_df.empty:
            filename = savepath + symbol + ".png"

            # Create figure
            fig, ax1 = plt.subplots(figsize=(12, 4))

            x = security_df["Date"]
            y1 = security_df["adj_close"]

            y1_upper_CI = security_df["adj_close_high"]
            y1_lower_CI = security_df["adj_close_low"]

            y2 = security_df["Volume"]
            y3 = security_df["adj_close_100_days_average"]

            plt.title(security.name + " (" + security.type + ")")

            plt.ylabel("Adj. close (1 / stock)")
            #ax2 = ax1.twinx()
            ax1.plot(x, y3, '-', alpha=0.7, color=(0, 0, 1), label="100 days average")
            ax1.plot(x, y1, ',-', alpha=0.9, color=(0, 0, .2), label=security.name + u"\u00B1" + "95% CI")
            ax1.fill_between(x, y1_lower_CI, y1_upper_CI, color=(0.2,0.3,0.4), alpha=.1)

            #ax2.plot(x, y2, ',-', color=(1, 0, 0), alpha=0.45)
            #plt.ylabel("Trade volume (1 / day)")

            ax1.legend(loc = 'best', frameon=False)

            # Create folder if not exists
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            # Save figure
            plt.savefig(filename, dpi = 600)
            print("Saved %s" % (filename))
