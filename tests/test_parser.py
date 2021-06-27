import os
import pytest
from app import db, create_app
from app.controllers import (
    CSXParser,
    UnionParser,
    KansasCitySouthernParser,
    CanadianNationalParser,
)
from app.controllers import CanadianPacificParser, NorfolkSouthernParser, BNSFParser
from app.models import Company

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSX_TEST_DATA_FILE = os.path.join(BASE_DIR, "data/csx_2021-Week-23-AAR.pdf")
UNION_TEST_DATA_FILE = os.path.join(BASE_DIR, "data/pdf_unp_week_16_carloads.pdf")
UNION_TEST_DATA_FILE2 = os.path.join(BASE_DIR, "data/pdf_unp_week_3_2021_carloads.pdf")
KANSAS_CITY_SOUTHERN_TEST_DATA_FILE = os.path.join(
    BASE_DIR, "data/week-17-05-01-2021-aar-carloads.pdf"
)
# CANADIAN_NATIONAL_TEST_DATA_FILE = os.path.join(BASE_DIR, "data/Week23_CN.xlsx")
CANADIAN_NATIONAL_TEST_DATA_FILE = os.path.join(BASE_DIR, "data/Week24_CN.xlsx")
CANADIAN_PACIFIC_TEST_DATA_FILE = os.path.join(
    BASE_DIR, "data/CP-Weekly-RTMs-and-Carloads-(14).xlsx"
)
NORFOLK_SOUTHERN_TEST_DATA_FILE = os.path.join(
    BASE_DIR, "data/investor-weekly-carloads-january-2021.pdf"
)
BNSF_TEST_DATA_FILE = os.path.join(BASE_DIR, "data/20210612_bnsf.pdf")


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
    # COMPANY_ID = "CSX_2020_1_1"
    # parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    parsed_data = Company.query.all()
    assert parsed_data
    # assert len(parsed_data) == 22


def test_union_parser(client):
    parser = UnionParser(2021, 2)
    with open(UNION_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
    # COMPANY_ID = "Union_Pacific_2021_2_1"
    # parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    parsed_data = Company.query.all()
    assert parsed_data
    # assert len(parsed_data) == 18


def test_union_parser2(client):
    parser = UnionParser(2021, 3)
    with open(UNION_TEST_DATA_FILE2, "rb") as file:
        parser.parse_data(file=file)
    # COMPANY_ID = "Union_Pacific_2021_2_1"
    # parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    parsed_data = Company.query.all()
    assert parsed_data
    # assert len(parsed_data) == 18


def test_kansas_city_southern_parser(client):
    parser = KansasCitySouthernParser(2021, 2)
    with open(KANSAS_CITY_SOUTHERN_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
    if Company.query.filter(Company.company_id == "Grain"):
        consolidate = Company.query.filter(Company.carloads).first()
        assert consolidate.carloads
        if consolidate.carloads == 3721:
            assert consolidate.carloads
        # else:
        #     assert 'error'
    parsed_data = Company.query.all()
    assert parsed_data
    # COMPANY_ID = "Kansas_City_Southern_2021_2_1"
    # parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    # assert len(parsed_data) == 22


def test_canadian_national_parser(client):
    parser = CanadianNationalParser(2021, 2)
    with open(CANADIAN_NATIONAL_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
    # COMPANY_ID = "Canadian_National_2021_2_1"
    # parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    parsed_data = Company.query.all()
    assert parsed_data
    # assert len(parsed_data) == 22


def test_bnsf_parser(client):
    parser = BNSFParser(2021, 2)
    with open(BNSF_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
    # COMPANY_ID = "BNSF_2021_2_1"
    # parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    parsed_data = Company.query.all()
    assert parsed_data
    assert len(parsed_data) == 25


def test_canadian_pacific_parser(client):
    parser = CanadianPacificParser(2021, 21)
    with open(CANADIAN_PACIFIC_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
    # COMPANY_ID = "Canadian_Pacific_2021_2_1"
    # parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    parsed_data = Company.query.all()
    assert parsed_data
    # assert len(parsed_data) == 5


def test_norfolk_southern_parser(client):
    parser = NorfolkSouthernParser(2021, 2)
    with open(NORFOLK_SOUTHERN_TEST_DATA_FILE, "rb") as file:
        parser.parse_data(file=file)
    # COMPANY_ID = 'Norfolk_Southern_2021_4_1'
    # parsed_data = Company.query.filter(Company.company_id == COMPANY_ID).all()
    parsed_data = Company.query.all()
    assert parsed_data
    # assert len(parsed_data) == 21
