import database as db


class Index(db.Base):
    """ Class to store index data
    Parameters:
        name (string): name of index
        symbol (string): unique symbol
        start_date (datetime.date): start date of index
        last_date (datetime.date): last available date of index
    """
    __tablename__ = 'index'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    symbol = db.Column(db.String)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    last_date = db.Column(db.DateTime)

    def __repr__(self):
        return self.name


class Quotation(db.Base):

    __tablename__ = 'quotations'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    open = db.Column(db.Numeric(10, 2))
    high = db.Column(db.Numeric(10, 2))
    low = db.Column(db.Numeric(10, 2))
    close = db.Column(db.Numeric(10, 2))
    volume = db.Column(db.Numeric(10, 2))
    index_id = db.Column(db.Integer, db.ForeignKey('index.id'))
    index = db.relationship('Index', backref='quotations')
