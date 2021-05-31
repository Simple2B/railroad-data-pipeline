# import re
import tempfile
from dateparser.search import search_dates
from datetime import datetime
import time
from urllib.request import urlopen
import pandas as pd
from sqlalchemy import and_
from .base_parser import BaseParser
from bs4 import BeautifulSoup
from selenium import webdriver
from config import BaseConfig as conf
from .carload_types import find_carload_id, ALL_PROD_TYPES
from app.models import Company
from app.logger import log


class CanadianPacificParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "https://investor.cpr.ca/key-metrics/default.aspx"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream
        self.link = None

    def scrapper(self, week: int, year: int) -> str or None:
        if conf.CURRENT_WEEK - 1 != week or conf.CURRENT_YEAR != year:
            log(log.WARNING, "Links not found")
            return None
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        browser = webdriver.Chrome(
            options=options, executable_path=conf.CHROME_DRIVER_PATH
        )
        log(log.INFO, "Start get url Canadian Pacific")
        browser.get(self.URL)
        log(log.INFO, "Got url Canadian Pacific")
        generated_html = browser.page_source
        soup = BeautifulSoup(generated_html, "html.parser")
        tags = soup.find_all("a", class_="button-link")
        while len(tags) != 2:
            browser.get(self.URL)
            generated_html = browser.page_source
            soup = BeautifulSoup(generated_html, "html.parser")
            tags = soup.find_all("a", class_="button-link")
            time.sleep(1)
        link = tags[0].attrs["href"]
        date = link.split("/")
        scrap_week = datetime(
            year=int(date[6]), month=int(date[7]), day=int(date[8])
        ).isocalendar()[1]
        if week == scrap_week and int(date[6]) == year:
            log(log.INFO, "Found pdf link: [%s]", link)
            return link

    def get_file(self) -> bool:
        file_url = self.scrapper(self.week_no, self.year_no)
        if file_url is None:
            return False
        file = urlopen(file_url)
        self.file = tempfile.NamedTemporaryFile(mode="wb+")
        for line in file.readlines():
            self.file.write(line)
        self.file.seek(0)
        return True

    def parse_data(self, file=None):
        if not file:
            file = self.file

        # Load spreadsheet
        file_xlsx = pd.ExcelFile(file)
        log(log.INFO, "--------Read xlsx file Canadian Pacific--------")
        read_xlsx = pd.read_excel(file_xlsx, header=None)
        xlsx_dicts = read_xlsx.to_dict("records")
        log(log.INFO, "--------Get xlsx text Canadian Pacific--------")

        data_dicts = []

        xlsx_date = xlsx_dicts.pop(2)[1].replace("-", "")

        dates = search_dates(xlsx_date)
        date = []

        for x in dates[0]:
            date.append(x)

        date = date[1]

        for xlsx_dict in xlsx_dicts:
            type_name = xlsx_dict[1]
            if type_name and type_name in ALL_PROD_TYPES:
                data_dicts.append(xlsx_dict)

        # list of all products
        products = {}

        for data in data_dicts:
            products[data[1]] = dict(
                week=dict(
                    current_year=data[2],
                    previous_year=data[3],
                    chg=round(data[5] * 100, 1),
                ),
                QUARTER_TO_DATE=dict(
                    current_year=data[12],
                    previous_year=data[13],
                    chg=round(data[15] * 100, 1),
                ),
                YEAR_TO_DATE=dict(
                    current_year=data[17],
                    previous_year=data[18],
                    chg=round(data[20] * 100, 1),
                ),
            )

        # write data to the database
        for prod_name, product in products.items():
            company_id = ""
            carload_id = find_carload_id(prod_name)
            company_id = f"Canadian_Pacific_{self.year_no}_{self.week_no}_{carload_id}"
            company = Company.query.filter(
                and_(
                    Company.company_id == company_id, Company.product_type == prod_name
                )
            ).first()

            if not company and carload_id is not None:
                Company(
                    company_id=company_id,
                    carloads=product["week"]["current_year"],
                    YOYCarloads=product["week"]["current_year"]
                    - product["week"]["previous_year"],
                    QTDCarloads=product["QUARTER_TO_DATE"]["current_year"],
                    YOYQTDCarloads=product["QUARTER_TO_DATE"]["current_year"]
                    - products[prod_name]["QUARTER_TO_DATE"]["previous_year"],
                    YTDCarloads=products[prod_name]["YEAR_TO_DATE"]["current_year"],
                    YOYYDCarloads=products[prod_name]["YEAR_TO_DATE"]["current_year"]
                    - products[prod_name]["YEAR_TO_DATE"]["previous_year"],
                    date=date,
                    week=self.week_no,
                    year=self.year_no,
                    company_name="Canadian Pacific",
                    product_type=prod_name,
                ).save()
        log(log.INFO, "-------- Write data to the database Canadian Pacific --------")
