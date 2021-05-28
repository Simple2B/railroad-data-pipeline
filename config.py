import os
import datetime
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"))


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = "Simple Flask App"
    DEBUG_TB_ENABLED = False
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "Ensure you set a secret key, this is important!"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

    CHROME_DRIVER_PATH = os.environ.get("CHROME_DRIVER_PATH", None)

    BEGIN_YEAR = int(os.environ.get("BEGIN_YEAR", "2021"))
    CURRENT_YEAR = datetime.datetime.now().year
    CURRENT_WEEK = datetime.datetime.now().date().isocalendar()[1]

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "email-smtp.us-east-2.amazonaws.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    # MAIL_DEBUG =
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "AKIARBQLSALC7H5MZJ5D")
    MAIL_PASSWORD = os.environ.get(
        "MAIL_PASSWORD", "BGh4folV6Gr0o4r7gjD8zqn9FPM9Ew0LrEBh0HwEnEKC"
    )
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER", "simple2b.mailer@gmail.com"
    )
    MAIL_ASCII_ATTACHMENTS = False

    @staticmethod
    def configure(app):
        # Implement this method to do further configuration on your app.
        pass


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEVEL_DATABASE_URL",
        "sqlite:///" + os.path.join(base_dir, "database-devel.sqlite3"),
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "sqlite:///" + os.path.join(base_dir, "database-test.sqlite3"),
    )


class ProductionConfig(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(base_dir, "database.sqlite3")
    )
    WTF_CSRF_ENABLED = True


config = dict(
    development=DevelopmentConfig, testing=TestingConfig, production=ProductionConfig
)
