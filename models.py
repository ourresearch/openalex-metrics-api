from app import db
from sqlalchemy.dialects.postgresql import JSONB

class Sample(db.Model):
    __tablename__ = 'samples'
    name = db.Column(db.Text, primary_key=True)
    entity = db.Column(db.Text)
    type = db.Column(db.Text)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    ids = db.Column(db.JSON)


class MetricSet(db.Model):
    __tablename__ = 'metric_sets'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Text)
    entity = db.Column(db.Text)
    date = db.Column(db.DateTime)
    data = db.Column(JSONB)
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "entity": self.entity,
            "date": self.date,
            "data": self.data
        }
    

class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Text, primary_key=True)
    entity = db.Column(db.Text)
    date = db.Column(db.DateTime)
    prod = db.Column(JSONB)
    walden = db.Column(JSONB)
    match = db.Column(JSONB)
    
    def to_dict(self):
        return {
            "id": self.id,
            "entity": self.entity,
            "date": self.date,
            "prod": self.prod,
            "walden": self.walden,
            "match": self.match
        }
        