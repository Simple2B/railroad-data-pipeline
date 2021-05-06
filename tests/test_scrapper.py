import pytest
from app.controllers import CSXParser, scrapper
from config import BaseConfig as conf


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_scrapper():
    scrapper("csx", 20, 2020, "https://investors.csx.com/metrics/default.aspx")
    assert scrapper


@pytest.mark.skipif(not conf.CHROME_DRIVER_PATH, reason="ChromeDriver not configured")
def test_csx_scrapper():
    csx = CSXParser(2020, 25)
    assert csx
    assert csx.file is None
    assert csx.get_file()
    assert csx.file
