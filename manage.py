from manager import Manager
from util import IndexList, DataController
from datetime import date
from model import Security, Exchange, DataVendor, Quotation
from database import db_session, db_engine, Base


manager = Manager()

dc = DataController() 


@manager.command
def createdb():
    """ creates the sqlite-databse"""
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)


@manager.command
def initdb():
    """ inits the sqlite-databse"""
    add_data_vendor("Yahoo", "www.yahoo.com")
    add_securities("indicesyahoo.csv")


@manager.command
def add_data_vendor(name, website):
    dc.add_data_vendor(name, website)


@manager.command
def add_securities(csvfile):
    """adds a list of securities from csv-data"""
    dc.add_security_from_csv(csvfile)


@manager.command
def list_all_securities():
    """ lists all saved db securities"""
    securities = db_session.query(Security).all()
    for s in securities:
        print(s)


@manager.command
def list_all_datavendors():
    """ lists all saved datavendors"""
    datavendors = db_session.query(DataVendor).all()
    for d in datavendors:
        print(d)


@manager.command
def list_prices_security(symbol):
    """ lists all saved quotes by symbol"""

    # Get Security object for given symbol
    security = db_session.query(Security).filter_by(symbol=symbol).one()
    if security is not None:
        quotations = db_session.query(Quotation).filter_by(security_id=
                                                       security.id).all()
        for quotation in quotations:
            print(quotation)
    else:
        print("Security " + symbol + " does not exist in db")


@manager.command
def update_price(symbol, datavendor = "Yahoo"):
    """update prices for one Security
        Default start_date: 2000/01/01"""
    dc.update_quotation(symbol, datavendor)


@manager.command
def update_price_all(datavendor = "Yahoo"):
    """update prices for all securities found in table 'security'
        Default start_date: 2000/01/01"""
    securities = db_session.query(Security).all()
    for s in securities:
        dc.update_quotation(s.symbol, datavendor)


@manager.command
def show_quotations_symbol(symbol):
    pass

@manager.command
def plot_security(symbol):
    dc.plot_security(symbol)

@manager.command
def plot_all_securities():
    securities = db_session.query(Security).all()
    for s in securities:
        dc.plot_security(s.symbol)

if __name__ == '__main__':
    manager.main()
    db_session.close()
