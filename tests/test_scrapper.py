import pytest
from app.controllers import scrapper, CSXParser, UnionParser, KansasCitySouthernParser, BNSFParser
from app.controllers import scrapper, CSXParser, UnionParser, KansasCitySouthernParser, CanadianNationalParser
from config import BaseConfig as conf


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_scrapper():
    scrap = scrapper("csx", 20, 2020, "https://investors.csx.com/metrics/default.aspx")
    assert scrap
    scrap = scrapper(
        "union",
        12,
        2021,
        "https://www.up.com/investor/aar-stb_reports/2021_Carloads/index.htm",
    )
    assert scrap
    scrap = scrapper("kansas_city_southern", 2, 2021,
                     "https://investors.kcsouthern.com/performance-metrics/aar-weekly-carload-report/2021?sc_lang=en")
    assert scrap
    scrap = scrapper(
        "bnsf", 2, 2021, "http://www.bnsf.com/about-bnsf/financial-information/index.html#Weekly+Carload+Reports")
    scrap = scrapper("canadian_national", 2, 2021, "https://www.cn.ca/en/investors/key-weekly-metrics/")
    assert scrap


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_csx_scrapper():
    csx = CSXParser(2020, 25)
    assert csx
    assert csx.file is None
    assert csx.get_file()
    assert csx.file


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_union_scraper():
    union = UnionParser(2021, 15)
    assert union
    assert union.file is None
    assert union.get_file()
    assert union.file


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_kansas_city_southern_scraper():
    kansas_city_southern = KansasCitySouthernParser(2021, 1)
    assert kansas_city_southern
    assert kansas_city_southern.file is None
    assert kansas_city_southern.get_file()
    assert kansas_city_southern.file


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_bnsf_scraper():
    bnsf = BNSFParser(2021, 1)
    assert bnsf
    assert bnsf.file is None
    assert bnsf.get_file()
    assert bnsf.file
def test_canadian_national_scraper():
    canadian_national = CanadianNationalParser(2021, 1)
    assert canadian_national
    assert canadian_national.file is None
    assert canadian_national.get_file()
    assert canadian_national.file
