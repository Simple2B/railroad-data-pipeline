from datetime import datetime

from app import db
from app.models.utils import ModelMixin


class Passed(db.Model, ModelMixin):

    __tablename__ = "passes"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    week = db.Column(db.Integer)
    year = db.Column(db.Integer)
    company_name = db.Column(db.String)
