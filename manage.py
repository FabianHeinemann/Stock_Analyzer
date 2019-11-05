from manager import Manager
from model import Index
from model import IndexList
from database import db
from datetime import date
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sqlalchemy


manager = Manager()
Session = sessionmaker(bind=db)
session = Session()
metadata = sqlalchemy.MetaData()


@manager.command
def initdb(db_type, test=False):
    """ inits the sqlite-databse"""
    metadata.drop_all(db)
    metadata.create_all(db)
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
    indices = session.query().all()
    print(indices)


if __name__ == '__main__':
    manager.main()
    session.close()
