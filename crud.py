from database import db


class Crud:

    def save(self):
        if self.id is None:
            db_session.add(self)
        return db_session.commit()

    def delete(self):
        db_session.delete()
        return db_session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
