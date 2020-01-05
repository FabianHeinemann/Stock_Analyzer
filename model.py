import database as db
from database import db_engine, db_session
import pandas as pd
import sqlalchemy as sa

class Security(db.Base):
    """ Class of a security data object (i.e. a general financial object
        such as an index or stock)
    """
    __tablename__ = 'security'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    type = db.Column(db.String)
    symbol = db.Column(db.String)
    created_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return (str(self.name) + ": " + str(self.symbol) + " (" + str(self.type) + ")")


class Exchange(db.Base):
    """ Class of an exchange data object
    """

    __tablename__ = 'exchange'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    currency = db.Column(db.String)
    created_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)


class DataVendor(db.Base):
    """ Class of an datavendor object (e.g. Yahoo)
    """

    __tablename__ = 'datavendor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    website = db.Column(db.String)
    created_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return (self.name + " " + self.website + " (" + str(self.last_updated) + ")")


class Quotation(db.Base):
    """ Class of a quotation object (security [e.g. stock or index] information on a given date)
    """

    __tablename__ = 'quotations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    open = db.Column(db.Numeric(10, 2))
    high = db.Column(db.Numeric(10, 2))
    low = db.Column(db.Numeric(10, 2))
    close = db.Column(db.Numeric(10, 2))
    adj_close = db.Column(db.Numeric(10, 2))
    volume = db.Column(db.Numeric(10, 2))
    created_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)
    data_vendor_id = db.Column(db.Integer, db.ForeignKey('datavendor.id'))
    data_vendor = db.relationship('DataVendor', backref='datavendor')
    security_id = db.Column(db.Integer, db.ForeignKey('security.id'))
    security = db.relationship('Security', backref='security')

    @classmethod
    def get_dataframe(cls, symbol):
        """ Get Pandas Dataframe of quotations for given symbol
        Args:
            symbol (string): Symbol of security (e.g. "^DJI")
        returns:
            Panadas dataframe

            None in case of error
        """

        return_df = None

        # Get security object for given symbol
        security = db_session.query(Security).filter_by(symbol=symbol).first()

        if security is not None:
            # Get quotation data for symbol as dataframe
            t = sa.Table(cls.__tablename__, sa.MetaData(), autoload_with=db_engine)
            return_df = pd.read_sql(t.select().where(t.c.security_id == security.id), db_engine)

        return return_df

    def __repr__(self):
        return (str(self.date) + ": " + str(self.adj_close) +
                "(" + str(self.volume) + ")")