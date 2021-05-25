#!/user/bin/env python
import os
import datetime
import click
import time

from app import create_app, db, models
from app.logger import log


app = create_app()
BEGIN_YEAR = int(os.environ.get("BEGIN_YEAR", "2019"))
CURRENT_YEAR = datetime.datetime.now().year
CURRENT_WEEK = datetime.datetime.now().date().isocalendar()[1]


# flask cli context setup
@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, m=models)


@app.cli.command()
def create_db():
    """Create the configured database."""
    db.create_all()


@app.cli.command()
@click.confirmation_option(prompt="Drop all database tables?")
def drop_db():
    """Drop the current database."""
    db.drop_all()


@app.cli.command()
@click.confirmation_option(prompt="Drop all database tables?")
def reset_db():
    """Reset the current database."""
    db.drop_all()
    db.create_all()


@app.cli.command()
def scrap():
    """Scrapping all companies"""
    log(log.INFO, "Scrapper started")
    from app.controllers import (
        CSXParser,
<<<<<<< HEAD
        # UnionParser,
=======
        UnionParser,
>>>>>>> c9415d5b89d4566b8cc9906145d224b47ee11a65
        # NorfolkSouthernParser,
        # KansasCitySouthernParser,
        # CanadianNationalParser,
        # CanadianPacificParser,
        # BNSFParser,
    )
    from app.models import Passed

    for year in range(BEGIN_YEAR, CURRENT_YEAR):
        log(log.INFO, "----------------Year: %d", year)
        finish_week = CURRENT_WEEK if year == CURRENT_YEAR else 53
        for week in range(1, finish_week):
            log(log.INFO, "----------------Week %d", week)
            COMPANIES = {
                CSXParser: "CSX",
                # UnionParser: "Union Parser",
                # NorfolkSouthernParser: "Norfolk Southern",
                # KansasCitySouthernParser: "Kansas City Southern Parser",
                # CanadianNationalParser: "Canadian National Parser",
                # CanadianPacificParser: "CanadianPacificParser",
                # BNSFParser: "BNSF Parser",
            }
            for Parser, company_name in COMPANIES.items():
                p = (
                    Passed.query.filter(Passed.company_name == company_name)
                    .filter(Passed.year == year)
                    .filter(Passed.week == week)
                    .first()
                )
                if p:
                    log(log.INFO, "Already done for [%s]", company_name)
                    continue
                log(log.INFO, "Start parser %s", company_name)
                parser = Parser(year_no=year, week_no=week)
                parser.get_file()
                parser.parse_data()
                Passed(company_name=company_name, year=year, week=week).save()
                time.sleep(2)


if __name__ == "__main__":
    app.run()
