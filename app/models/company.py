from datetime import datetime

from app import db
from app.models.utils import ModelMixin


class Company(db.Model, ModelMixin):

    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.String)
    carloads = db.Column(db.Integer)
    QTDCarloads = db.Column(db.Integer, nullable=False)
    YOYQTDCarloads = db.Column(db.Integer, nullable=True)
    YTDCarloads = db.Column(db.Integer, nullable=False)
    YOYYDCarloads = db.Column(db.Integer, nullable=True)
    parse_date = db.Column(db.DateTime, default=datetime.now)
    week = db.Column(db.Integer)
    year = db.Column(db.Integer)
    company_name = db.Column(db.String)
    product_type = db.Column(db.String)
