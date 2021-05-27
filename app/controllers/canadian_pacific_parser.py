import re
import tempfile
from datetime import datetime
from urllib.request import urlopen
import pandas as pd
from sqlalchemy import and_
from .base_parser import BaseParser
from bs4 import BeautifulSoup
from selenium import webdriver
from config import BaseConfig as conf
from .carload_types import find_carload_id
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
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        browser = webdriver.Chrome(
            options=options, executable_path=conf.CHROME_DRIVER_PATH
        )
        browser.get(self.URL)
        generated_html = browser.page_source
        soup = BeautifulSoup(generated_html, "html.parser")
        tags = soup.find_all("a", class_="button-link")
        while len(tags) != 2:
            browser.get(self.URL)
            generated_html = browser.page_source
            soup = BeautifulSoup(generated_html, "html.parser")
            tags = soup.find_all("a", class_="button-link")
            self.file.sleep(1)
        link = tags[0].attrs["href"]
        date = link.split("/")
        scrap_week = datetime(
            year=int(date[6]), month=int(date[7]), day=int(date[8])
        ).isocalendar()[1]
        if week == scrap_week and int(date[6]) == year:
            log(log.INFO, "Found pdf link: [%s]", link)
            return link
        log(log.WARNING, "Links not found")
        return None

    def get_file(self) -> bool:
        file_url = self.scrapper(self.week_no, self.year_no, self.URL)
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

        if not self.file:
            log(log.ERROR, "Nothing to parse, file is not found")
            return None

        # Load spreadsheet
        file_xlsx = pd.ExcelFile(file)
        read_xlsx = pd.read_excel(file_xlsx, header=None)
        xlsx_dicts = read_xlsx.to_dict(orient="dictionary_xlsx")

        del xlsx_dicts[0]

        xlsx_dicts_types = xlsx_dicts.pop(1)

        # by type of carload value
        data_dicts = {}

        for j in xlsx_dicts_types:
            values_dict = []
            for index in xlsx_dicts:
                for i in xlsx_dicts[index]:
                    if j == i:
                        values_dict.append(xlsx_dicts[index][i])
            data_dicts.update({str(xlsx_dicts_types[j]): values_dict})

        del data_dicts["nan"]
        del data_dicts["Revenue Ton Miles (in millions)"]

        # list of all products
        products = {}

        for data in data_dicts:
            if data != "nan":
                products[data] = dict(
                    week=dict(
                        current_year=data_dicts[data][0],
                        previous_year=data_dicts[data][1],
                        chg=round(data_dicts[data][3] * 100, 1),
                    ),
                    QUARTER_TO_DATE=dict(
                        current_year=data_dicts[data][5],
                        previous_year=data_dicts[data][6],
                        chg=round(data_dicts[data][8] * 100, 1),
                    ),
                    YEAR_TO_DATE=dict(
                        current_year=data_dicts[data][10],
                        previous_year=data_dicts[data][11],
                        chg=round(data_dicts[data][13] * 100, 1),
                    ),
                )

        # get the date of report from the general dict
        months = dict(
            Jan=1,
            Feb=2,
            Mar=3,
            Apr=4,
            May=5,
            Jun=6,
            Jul=7,
            Aug=8,
            Sep=9,
            Oct=10,
            Nov=11,
            Dec=12,
        )

        products_keys = list(products.keys())
        date = products_keys[0]

        date_farmate = date.split(" ")
        day = date_farmate[7]
        year = date_farmate[8]
        month = date_farmate[6]
        format_month = ""

        for mon in months:
            if mon == month:
                format_month = months[mon]

        format_day = int(re.findall(r"(\d+)", day)[0])
        format_year = int(re.findall(r"(\d+)", year)[0])

        date_db = datetime(month=format_month, day=format_day, year=format_year)

        # write data to the database
        del products[products_keys[0]]
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
                    date=date_db,
                    week=self.week_no,
                    year=self.year_no,
                    company_name="Canadian National",
                    product_type=prod_name,
                ).save()
