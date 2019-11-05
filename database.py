from sqlalchemy import create_engine
import config
db = create_engine(config.SQLALCHEMY_DATABASE_URI)
