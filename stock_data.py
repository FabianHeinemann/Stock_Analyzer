import datetime
import sqlalchemy as db

class stock_data():

    def __init__(self):
        data_base_str = 'sqlite:///stock_data.db'
        self.engine = db.create_engine(data_base_str)
        self.connection = self.engine.connect()
    
    def update_database(self, start_date : datetime.date, end_date : datetime.date) -> bool:

        return True
    