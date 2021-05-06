from bs4 import BeautifulSoup
from selenium import webdriver
from config import BaseConfig as conf
from app.logger import log


def scrapper(company: str, week: int, year: int, url: str) -> str or None:
    """[Scrapper for railroad reports]

    Args:
        company (str): [company]
        week (int): [week]
        year (int): [year]
        url (str): [url for scrapping]
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options, executable_path=conf.CHROME_DRIVER_PATH)
    browser.get(url)
    generated_html = browser.page_source
    soup = BeautifulSoup(generated_html, 'html.parser')
    if company == "csx":
        links = soup.find_all('a', class_='module_link')
        for i in links:
            scrap_data = i.span.text.split()
            scrap_year = scrap_data[0]
            scrap_week = scrap_data[2]
            if scrap_year == str(year) and scrap_week == str(week):
                return i['href']
        log(log.WARNING, "Links not found")
        return None
