import os
import pytest

from app import db, create_app

from app.controllers import CSXParser, UnionParser, KansasCitySouthernParser


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSX_TEST_DATA_FILE = os.path.join(BASE_DIR, 'data/2020-Week-1-AAR.pdf')

UNION_TEST_DATA_FILE = os.path.join(BASE_DIR, 'data/pdf_unp_week_16_carloads.pdf')

KANSAS_CITY_SOUTHERN_TEST_DATA_FILE = os.path.join(BASE_DIR, 'data/week-17-05-01-2021-aar-carloads.pdf')


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
    parser = CSXParser(2020, 1)
    with open(CSX_TEST_DATA_FILE, "rb") as file:
        filePdf = parser.parse_data(file=file)
        assert filePdf


def test_union_parser(client):
    parser = UnionParser(2021, 2)
    with open(UNION_TEST_DATA_FILE, "rb") as file:
        filePdf = parser.parse_data(file=file)
        assert filePdf


def test_kansas_city_southern_parser(client):
    parser = KansasCitySouthernParser(2021, 2)
    with open(KANSAS_CITY_SOUTHERN_TEST_DATA_FILE, "rb") as file:
        filePdf = parser.parse_data(file=file)
        assert filePdf
