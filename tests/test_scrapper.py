import pytest
from app.controllers import CSXParser, scrapper, UnionParser
from config import BaseConfig as conf


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_scrapper():
    scrap = scrapper("csx", 20, 2020, "https://investors.csx.com/metrics/default.aspx")
    assert scrap
    scrap = scrapper("union", 12, 2021, "https://www.up.com/investor/aar-stb_reports/2021_Carloads/index.htm")
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
