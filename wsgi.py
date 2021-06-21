#!/user/bin/env python
import click

from flask_mail import Message
from app import create_app, db, models, mail
from app.logger import log, LOGGER_NAME
from app.controllers import data_scrap
from config import BaseConfig as conf


app = create_app()

# app.config.from_pyfile("config.cfg")


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


def run_scrap():
    try:
        data_scrap()
    except Exception as err:
        # send email on error
        import traceback
        body = f"Error {str(err)}\n"
        body += traceback.format_exc()
        msg = Message(subject="Error", body=body, recipients=conf.MAIL_RECIPIENTS.split(";"))
        log(log.INFO, "Mail sending...")
        with open(f"{LOGGER_NAME}.log", "r") as att:
            msg.attach(att.name, "text/plain", att.read())
        mail.send(msg)
        assert msg


@app.cli.command()
def scrap():
    """Scrapping all companies"""
    log(log.INFO, "Scrapper started")
    run_scrap()


if __name__ == "__main__":
    app.run()
