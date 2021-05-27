#!/user/bin/env python
from flask_mail import Mail, Message
import click

from app import create_app, db, models
from app.logger import log
from app.controllers import data_scrap


app = create_app()
mail = Mail(app)


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
    except Exception as err:
        # TODO: collect error data and send email
        msg = Message(err, sender="from@example.com", recipients=["to@example.com"])
        msg
        assert err


if __name__ == "__main__":
    app.run()
