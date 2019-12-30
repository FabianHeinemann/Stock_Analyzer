import database as db


class Security(db.Base):
    """ Class to store index data
    Parameters:
        name (string): name of index
        symbol (string): unique symbol
        start_date (datetime.date): start date of index
        last_date (datetime.date): last available date of index
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

    __tablename__ = 'exchange'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    currency = db.Column(db.String)
    created_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)


class DataVendor(db.Base):

    __tablename__ = 'datavendor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    website = db.Column(db.String)
    created_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return (self.name + " " + self.website + " (" + str(self.last_updated) + ")")


class Quotation(db.Base):

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
    Security = db.relationship('Security', backref='security')

    def __repr__(self):
        return (str(self.date) + ": " + str(self.adj_close) +
                "(" + str(self.volume) + ")")
