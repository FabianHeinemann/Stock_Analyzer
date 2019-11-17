from sqlalchemy import create_engine, Column, String, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import config
Base = declarative_base()
db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker())
db_session.configure(bind=db_engine)
