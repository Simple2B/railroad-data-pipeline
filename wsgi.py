#!/user/bin/env python
import os
import datetime
import click
import time

from app import create_app, db, models
from app.logger import log
from app.controllers import data_scrap


app = create_app()


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
    try:
        data_scrap()
    except Exception as e:
        # TODO: collect error data and send email
        assert e


if __name__ == "__main__":
    app.run()
