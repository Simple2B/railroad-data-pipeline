from time import sleep
import re
from datetime import datetime
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
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options, executable_path=conf.CHROME_DRIVER_PATH)
    browser.get(url)
    generated_html = browser.page_source
    soup = BeautifulSoup(generated_html, "html.parser")
    if company == "csx":
        links = soup.find_all("a", class_="module_link")
        while len(links) < 53:
            browser.get(url)
            generated_html = browser.page_source
            soup = BeautifulSoup(generated_html, "html.parser")
            links = soup.find_all("a", class_="module_link")
            sleep(1)
        for i in links:
            scrap_data = i.span.text.split()
            scrap_year = scrap_data[0]
            scrap_week = scrap_data[2]
            if scrap_year == str(year) and scrap_week == str(week):
                link = i["href"]
                log(log.INFO, "Found pdf link: [%s]", link)
                return link
        log(log.WARNING, "Links not found")
        return None
    elif company == "union":
        links = soup.find_all("a", class_="pdf")
        for i in links:
            scrap_data = i.text.split()
            scrap_week = scrap_data[1]
            if str(week) == scrap_week:
                link = "https://www.up.com" + i["href"]
                log(log.INFO, "Found pdf link: [%s]", link)
                return link
        log(log.WARNING, "Links not found")
        return None
    elif company == "kansas_city_southern":
        links = soup.find_all("a", class_="ext-link")
        for i in links:
            if len(str(week)) == 1:
                week = f"0{week}"
            scrap_data = i.attrs["href"].split("/")[6]
            scrap_date = scrap_data.split("-")
            scrap_week = scrap_date[1]
            scrap_year = scrap_date[4]
            if str(week) == scrap_week and str(year) == scrap_year:
                link = "https://investors.kcsouthern.com" + i.attrs["href"]
                log(log.INFO, "Found pdf link: [%s]", link)
                return link
        log(log.WARNING, "Links not found")
        return None
    elif company == "canadian_national":
        return None
    elif company == "bnsf":
        links = soup.find_all("a", class_="local-link")
        links_pdf = []
        for link in links:
            a = link.attrs["href"].split("/")[-1].split(".")[-1]
            text = link.text
            match = re.search(r"\d{2}\/\d{2}\/\d{4}", text)
            if a == "pdf" and match:
                links_pdf.append(link)
        for i in links_pdf:
            scrap_date = i.text.split("/")
            date = datetime(
                month=int(scrap_date[0]),
                day=int(scrap_date[1]),
                year=int(scrap_date[2]),
            )
            scrap_week = date.isocalendar()[1]
            if week == scrap_week and int(scrap_date[2]) == year:
                link = "http://www.bnsf.com" + i["href"]
                log(log.INFO, "Found pdf link: [%s]", link)
                return link
        log(log.WARNING, "Links not found")
        return None
    elif company == "norfolk_southern":
        tags = soup.find_all("a")
        link = [
            link.attrs["href"]
            for link in tags
            if "weekly-performance-reports/AAR_Categories" in link.attrs["href"]
        ]
        time = datetime.now()
        scrap_week = time.isocalendar()[1]
        scrap_year = time.isocalendar()[0]
        if week == scrap_week and scrap_year == year:
            link = "http://www.nscorp.com" + link[0]
            log(log.INFO, "Found pdf link: [%s]", link)
            return link
        log(log.WARNING, "Links not found")
        return None
