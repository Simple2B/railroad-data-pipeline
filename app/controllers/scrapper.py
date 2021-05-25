import time
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
        while len(links) < 53:
            browser.get(url)
            generated_html = browser.page_source
            soup = BeautifulSoup(generated_html, 'html.parser')
            links = soup.find_all('a', class_='module_link')
            time.sleep(1)
        for i in links:
            scrap_data = i.span.text.split()
            scrap_year = scrap_data[0]
            scrap_week = scrap_data[2]
            if scrap_year == str(year) and scrap_week == str(week):
                link = i['href']
                log(log.INFO, "Found pdf link: [%s]", link)
                return link
        log(log.WARNING, "Links not found")
        return None
    elif company == 'union':
        links = soup.find_all('a', class_='pdf')
        for i in links:
            scrap_data = i.text.split()
            scrap_week = scrap_data[1]
            if str(week) == scrap_week:
                link = "https://www.up.com" + i['href']
                log(log.INFO, "Found pdf link: [%s]", link)
                return link
        log(log.WARNING, "Links not found")
        return None
    elif company == 'kansas_city_southern':
        links = soup.find_all('a', class_='ext-link')
        for i in links:
            scrap_data = i.text.split()
            scrap_week = scrap_data[1]
            if str(week) == scrap_week:
                return "https://investors.kcsouthern.com" + i['href']
        log(log.WARNING, "Links not found")
        return None
    elif company == 'canadian_national':
        years_of_reports = soup.find_all('select', id="select1")
        for year in years_of_reports:
            if year:
                links = soup.find_all('select', id="select2")
                for i in links:
                    scrap_data = i.text.split()
                    scrap_week = scrap_data[1]
                    if str(week) == scrap_week:
                        return "https://www.cn.ca" + i['value']
        log(log.WARNING, "Links not found")
        return None
