from config import *

class Data(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    datetimestr = db.Column(db.Text)
    user = db.Column(db.Text)
    images = db.Column(db.Text)

    def __init__(self,datetimestr, user, images):
        self.datetimestr = datetimestr
        self.user = user
        self.images = images

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def delete(cls, datetimestr, user):
        res = db.session.query(Data).filter(Data.user == user, Data.datetimestr == datetimestr).delete()
        db.session.commit()
        return res