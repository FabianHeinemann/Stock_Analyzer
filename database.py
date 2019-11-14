from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import config
db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker())
db_session.configure(bind=db_engine)
