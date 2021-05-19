import os
import pytest

from app import db, create_app

from app.controllers import CSXParser, UnionParser, KansasCitySouthernParser, BNSFParser
from app.controllers import CanadianNationalParser
from app.models import Company


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSX_TEST_DATA_FILE = os.path.join(BASE_DIR, 'data/2020-Week-1-AAR.pdf')
UNION_TEST_DATA_FILE = os.path.join(BASE_DIR, 'data/pdf_unp_week_16_carloads.pdf')
KANSAS_CITY_SOUTHERN_TEST_DATA_FILE = os.path.join(BASE_DIR, 'data/week-17-05-01-2021-aar-carloads.pdf')
BNSF_TEST_DATA_FILE = os.path.join(BASE_DIR, 'data/20210501.pdf')
CANADIAN_NATIONAL_TEST_DATA_FILE = os.path.join(BASE_DIR, 'data/Week16.xlsx')


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
        parser.parse_data(file=file)
    COMPANY_ID = "CSX_2020_1_XX"
    parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    assert parsed_data
    assert len(parsed_data) == 25


def test_union_parser(client):
    parser = UnionParser(2021, 2)
    with open(UNION_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
    COMPANY_ID = "Union_Pacific_2021_2_XX"
    parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    assert parsed_data
    # assert len(parsed_data) == 25


def test_kansas_city_southern_parser(client):
    parser = KansasCitySouthernParser(2021, 2)
    with open(KANSAS_CITY_SOUTHERN_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
    COMPANY_ID = "Kansas_City_Southern_2021_2_XX"
    parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    assert parsed_data
    assert len(parsed_data) == 24


def test_bnsf_parser(client):
    parser = BNSFParser(2021, 2)
    with open(BNSF_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
    COMPANY_ID = "BNSF_2021_2_XX"
    parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    assert parsed_data
    assert len(parsed_data) == 25


def test_canadian_national_parser(client):
    parser = CanadianNationalParser(2021, 2)
    with open(CANADIAN_NATIONAL_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
    COMPANY_ID = "Canadian_National_2021_2_XX"
    parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    assert parsed_data
    assert len(parsed_data) == 19
