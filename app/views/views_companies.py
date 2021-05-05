from flask import render_template, Blueprint

companies_blueprint = Blueprint("companies", __name__)


@companies_blueprint.route("/")
def companies_report():
    return render_template("companies.html")
