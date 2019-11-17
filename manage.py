from manager import Manager
from util import IndexList
from datetime import date
from model import Index, Quotation
from database import db_session, db_engine, Base


manager = Manager()


@manager.command
def createdb():
    """ creates the sqlite-databse"""
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)

@manager.command
def initdb(db_type, test=False):
    """ inits the sqlite-databse"""
    from database import db_session, db_engine
    index_list = IndexList(date(2019, 10, 22),
                           date(2019, 10, 29))
    if test:
        index_list.initialize_indexes(source="test")
        #index_list.serialize_indexes(target="db")
    else:
        index_list.initialize_indexes(source="test")


@manager.command
def listindex():
    """ lists all saved db indices"""
    indices = db_session.query(Index).all()
    print(indices)


if __name__ == '__main__':
    manager.main()
    from database import db_session, db_engine
    db_session.close()
