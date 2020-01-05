from manager import Manager
from util import DataController
import model as model
from model import Security, Exchange, DataVendor, Quotation
from database import db_session, db_engine, Base
from datetime import datetime, timedelta, date

manager = Manager()

dc = DataController()


@manager.command
def create_db():
    """Creates the sqlite-databse"""
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)


@manager.command
def init_db():
    """Inits the sqlite-database"""
    add_data_vendor("Yahoo", "www.yahoo.com")
    add_securities("indicesyahoo.csv")
    add_securities("stocks.csv")


@manager.command
def add_data_vendor(name, website):
    """Add a new datavendor given as argument <name>"""
    dc.add_data_vendor(name, website)


@manager.command
def add_securities(csvfile):
    """Adds a list of securities from argument <csv-data>"""
    dc.add_security_from_csv(csvfile)


@manager.command
def list_all_securities():
    """Lists all saved db securities"""
    securities = db_session.query(Security).all()
    for s in securities:
        print(s)


@manager.command
def list_all_datavendors():
    """Lists all saved data vendors for securities data."""

    # Get datavendors
    datavendors = db_session.query(DataVendor).all()
    for d in datavendors:
        print(d.name)


@manager.command
def list_prices(symbol):
    """Lists saved quotes for security given as argument <symbol>."""

    # Get Security object
    security = db_session.query(Security).filter_by(symbol=symbol).one()
    if security is not None:
        quotations = db_session.query(Quotation).filter_by(security_id=security.id).all()
        for quotation in quotations:
            print(quotation)
    else:
        print("Security " + symbol + " does not exist in db")


@manager.command
def update_quote(symbol, datavendor="Yahoo"):
    """Update quotes for the security given as argument <symbol>. Latest missing dates are updated."""
    latest_date = dc.get_latest_update(symbol)
    if latest_date < date.today():
        dc.update_quotation(symbol, datavendor, latest_date + timedelta(days=1))
    else:
        print("Security %s already up-to date, last update was: %s" % (symbol, latest_date.strftime("%Y-%m-%d")))


@manager.command
def update_all_quotes(datavendor="Yahoo"):
    """Update quotes for all securities found in table 'security', argument <symbol>. Latest missing dates are updated."""
    securities = db_session.query(Security).all()
    for s in securities:
        symbol = s.symbol
        latest_date = dc.get_latest_update(symbol)
        if latest_date < date.today():
            dc.update_quotation(symbol, datavendor, latest_date + timedelta(days=1))
        else:
            print("Security %s already up-to date, last update was: %s" % (symbol, latest_date.strftime("%Y-%m-%d")))


@manager.command
def plot(symbol):
    """Creates a plot for given security, argument <symbol> (i.e. an index)"""
    dc.plot_security(symbol)


@manager.command
def plot_all():
    """Creates a plot for each entry in table security"""
    securities = db_session.query(Security).all()
    for s in securities:
        dc.plot_security(s.symbol)

@manager.command
def test_strategy():
    """Creates a simple test over all indices"""
    indices = db_session.query(Security).filter_by(type="Index").all()
    dc.join_dataframes(indices)


@manager.command
def get_securities_pd():
    print(model.get_securities_by_type("index"))

@manager.command
def test():
    if Quotation.get_dataframe("^DJI") is not None:
        print(Quotation.get_dataframe("^DJI"))


if __name__ == '__main__':
    manager.main()
    db_session.close()
