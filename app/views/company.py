from flask import render_template, Blueprint
from app.models import Company

companies_blueprint = Blueprint("companies", __name__)


@companies_blueprint.route("/")
def companies_report():
    companies = Company.query.all()
    return render_template("companies.html", companies=companies)
