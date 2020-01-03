from manager import Manager
from util import DataController
from model import Security, Exchange, DataVendor, Quotation
from database import db_session, db_engine, Base

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
    """Lists all saved data vendors for securities data"""

    # Get datavendors
    datavendors = db_session.query(DataVendor).all()
    for d in datavendors:
        print(d.name)


@manager.command
def list_prices(symbol):
    """Lists saved quotes for security given as argument <symbol>"""

    # Get Security object
    security = db_session.query(Security).filter_by(symbol=symbol).one()
    if security is not None:
        quotations = db_session.query(Quotation).filter_by(security_id=security.id).all()
        for quotation in quotations:
            print(quotation)
    else:
        print("Security " + symbol + " does not exist in db")


@manager.command
def update_price(symbol, datavendor="Yahoo"):
    """Update prices for the security given as argument <symbol>. Default start_date: 2000/01/01"""
    dc.update_quotation(symbol, datavendor)


@manager.command
def update_price_all(datavendor="Yahoo"):
    """Update prices for all securities found in table 'security', argument <symbol>. Default start_date: 2000/01/01"""
    securities = db_session.query(Security).all()
    for s in securities:
        dc.update_quotation(s.symbol, datavendor)


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


if __name__ == '__main__':
    manager.main()
    db_session.close()
