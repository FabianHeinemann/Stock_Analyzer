from manager import Manager
from model import IndexList
from database import db_session, db_engine
from datetime import date
import sqlalchemy as sqlalchemy


manager = Manager()
metadata = sqlalchemy.MetaData()


@manager.command
def initdb(db_type, test=False):
    """ inits the sqlite-databse"""
    metadata.drop_all(db_engine)
    metadata.create_all(db_engine)
    index_list = IndexList(date(2019, 10, 22),
                           date(2019, 10, 29))
    if test:
        index_list.initialize_indexes(source="test")
        index_list.serialize_indexes(target="db")
    else:
        index_list.initialize_indexes(source="test")
        for index in index_list:
            # Object Mapping from classes to sqlite via sqlalchemy
            pass


@manager.command
def listindex():
    """ lists all saved db indices"""
    indices = db_session.query().all()
    print(indices)


if __name__ == '__main__':
    manager.main()
    db_session.close()
