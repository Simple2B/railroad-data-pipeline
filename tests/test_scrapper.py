import pytest
from app.controllers import (
    scrapper,
    CSXParser,
    UnionParser,
    KansasCitySouthernParser,
    CanadianNationalParser,
    CanadianPacificParser
)
from app.controllers import NorfolkSouthernParser, BNSFParser
from config import BaseConfig as conf


WEEK = conf.CURRENT_WEEK
YEAR = conf.CURRENT_YEAR


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_scrapper():
    scrap = scrapper(
        "csx", WEEK - 1, YEAR, "https://investors.csx.com/metrics/default.aspx"
    )
    assert scrap
    scrap = scrapper(
        "union",
        WEEK - 1,
        YEAR,
        "https://www.up.com/investor/aar-stb_reports/2021_Carloads/index.htm",
    )
    assert scrap
    scrap = scrapper(
        "kansas_city_southern",
        WEEK - 1,
        YEAR,
        "https://investors.kcsouthern.com/performance-metrics/aar-weekly-carload-report/2021?sc_lang=en",
    )
    assert scrap
    scrap = scrapper(
        "bnsf",
        WEEK - 2,
        YEAR,
        "http://www.bnsf.com/about-bnsf/financial-information/index.html#Weekly+Carload+Reports",
    )
    assert scrap
    scrap = scrapper(
        "canadian_national",
        WEEK,
        YEAR,
        "https://www.cn.ca/en/investors/key-weekly-metrics/",
    )
    assert scrap is None
    scrap = scrapper(
        "canadian_pacific",
        WEEK,
        YEAR,
        "https://investor.cpr.ca/key-metrics/default.aspx",
    )
    assert scrap
    scrap = scrapper(
        "norfolk_southern",
        WEEK,
        YEAR,
        "http://www.nscorp.com/content/nscorp/en/investor-relations/performance-metrics.html",
    )
    assert scrap


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_csx_scrapper():
    csx = CSXParser(YEAR, WEEK - 1)
    assert csx
    assert csx.file is None
    assert csx.get_file()
    assert csx.file


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_union_scraper():
    union = UnionParser(YEAR, WEEK - 1)
    assert union
    assert union.file is None
    assert union.get_file()
    assert union.file


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_kansas_city_southern_scraper():
    kansas_city_southern = KansasCitySouthernParser(YEAR, WEEK - 1)
    assert kansas_city_southern
    assert kansas_city_southern.file is None
    assert kansas_city_southern.get_file()
    assert kansas_city_southern.file


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_canadian_national_scraper():
    canadian_national = CanadianNationalParser(YEAR, WEEK)
    assert canadian_national
    assert canadian_national.file is None
    assert canadian_national.get_file()
    assert canadian_national.file


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_canadian_pacific_scraper():
    canadian_pacific = CanadianPacificParser(YEAR, WEEK)
    assert canadian_pacific
    assert canadian_pacific.file is None
    assert canadian_pacific.get_file()
    assert canadian_pacific.file


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_norfolk_southern_scraper():
    norfolk_southern = NorfolkSouthernParser(YEAR, WEEK)
    assert norfolk_southern
    assert norfolk_southern.file is None
    assert norfolk_southern.get_file()
    assert norfolk_southern.file


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_bnsf_scraper():
    bnsf = BNSFParser(YEAR, WEEK - 2)
    assert bnsf
    assert bnsf.file is None
    assert bnsf.get_file()
    assert bnsf.file
