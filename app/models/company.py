from datetime import datetime

from app import db
from app.models.utils import ModelMixin


class Company(db.Model, ModelMixin):

    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.String(64))
    carloads = db.Column(db.Integer)

    YOYCarloads = db.Column(db.Integer, nullable=True)
    QTDCarloads = db.Column(db.Integer, nullable=True)
    YOYQTDCarloads = db.Column(db.Integer, nullable=True)
    YTDCarloads = db.Column(db.Integer, nullable=True)
    YOYYDCarloads = db.Column(db.Integer, nullable=True)

    date = db.Column(db.DateTime, default=datetime.now)
    week = db.Column(db.Integer)
    year = db.Column(db.Integer)
    company_name = db.Column(db.String(64))
    carload_id = db.Column(db.Integer)
    product_type = db.Column(db.String(64))
