import os
import pytest

from app import db, create_app

from app.controllers import CSXParser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSX_TEST_DATA_FILE = os.path.join(BASE_DIR, 'data/2020-Week-1-AAR.pdf')


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_main_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_csx_parser(client):
    parser = CSXParser()
    with open(CSX_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
