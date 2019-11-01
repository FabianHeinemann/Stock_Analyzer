
#from database import db
import datetime
#from sqlalchemy import _or
import pandas as pd
import pandas_datareader as pdr
import pandas_datareader.data as web
from pandas_datareader.stooq import StooqDailyReader

class IndexList:

    START_DATE = datetime.datetime(2000, 1, 1)
    END_DATE = datetime.datetime(2019,10, 31)

    def __init__(self):
        self
        self.indices = []
        self.index_list = {'^AOR': 'All Ordinaries',
                        '^HSI': 'Hang Seng',
                        '^JCI': 'JCI',
                        '^KLCI': 'KLCI',
                        '^KOSPI': 'KOSPI',
                        '^NKX':	'NIKKEI225',
                        '^NZ50': 'NZX50',
                        '^PSEI': 'PSEI',
                        '^SET':	'SET',
                        '^SHBS':	'SSE B-SHARE',
                        '^SHC':	'SSE COMP',
                        '^SNX':	'SENSEX',
                        '^STI':	'STRAITS TIMES',
                        '^TWSE': 'TAIEX',
                        #'^ATX':	'ATX INDEX',
                        '^AEX':	'AEX',
                        '^ATH':	'ATHEX COMP',
                        '^BEL20':	'BEL20',
                        '^BET':	'BET',
                        '^BUX':	'BUX',
                        '^CAC':	'CAC40',
                        '^DAX':	'DAX',
                        '^FMIB':	'FTSE MIB',
                        '^FTM':	'FTSE250',
                        '^HEX':	'HEX',
                        '^IBEX':	'IBEX35',
                        '^ICEX':	'ICEX',
                        '^MDAX':	'MDAX',
                        '^MOEX':	'MOEX',
                        '^OMXR':	'OMX RIGA',
                        '^OMXS':	'OMX STOCKHOLM',
                        '^OMXT':	'OMX TALLINN',
                        '^OMXV':	'OMX VILNIUS',
                        '^OSEAX':	'OSE',
                        '^PSI20':	'PSI20',
                        '^PX':	'PX',
                        '^RTS':	'RTS',
                        '^SAX':	'SAX',
                        '^SDXP':	'SDAX',
                        '^SMI':	'SMI',
                        '^SOFIX':	'SOFIX',
                        '^TDXP':	'TECDAX',
                        '^UKX':	'UK100',
                        '^UX': 'UX',
                        #'WIG20':	'WIG20',
                        '^XU100':	'XU100',
                        '^BVP':	'BOVESPA',
                        '^DJC':	'DOW JONES COMP',
                        '^DJI':	'DOW JONES INDU',
                        '^DJT':	'DOW JONES TRANS',
                        '^DJU':	'DOW JONES UTIL',
                        '^IPC':	'IPC',
                        '^IPSA':	'IPSA',
                        '^MRV':	'MERVAL',
                        '^NDQ':	'NASDAQ COMP',
                        '^NDX':	'NASDAQ100',
                        '^SPX':	'S&P500',
                        '^TSX':	'S&P/TSX COMP',
                        '^CRY':	'CRB INDEX'
                        }

    def list_indices(self):
        return self.indices


    def initialise_indices(self):
        for symbol in self.index_list:
            print(symbol)
            stooq_data = self.get_stooq_data(symbol)
            new_index = Index(self.index_list.get(symbol), symbol, stooq_data.index[-1], stooq_data.index[0])
            new_index.define_quotations(stooq_data)
            self.indices.append(new_index)

    def get_stooq_data(self, symbol):
        return StooqDailyReader(
            symbols=symbol,
            start=self.START_DATE,
            end=self.END_DATE,
            chunksize=25,
            retry_count=3,
            pause=0.1,
            session=None
        ).read()






class Index:

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
        print("from: " + self.start_date + " to: " + self.last_date)
        print(self.quotation_df)
        print("")


list = IndexList()
list.initialise_indices()
indices = list.list_indices()
for i in indices:
    print(i)
