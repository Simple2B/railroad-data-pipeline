import tempfile
import re

# from dateparser.search import search_dates
from datetime import datetime, date
import time
from urllib.request import urlopen
import pandas as pd

# from openpyxl import load_workbook
from sqlalchemy import and_

# from sqlalchemy.sql.expression import update
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
        if (
            conf.CURRENT_WEEK - 1 != week
            and conf.CURRENT_WEEK != week
            or conf.CURRENT_YEAR != year
        ):
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
        log(log.INFO, "Read xlsx file Canadian Pacific")
        read_xlsx = pd.read_excel(file_xlsx, sheet_name=1)
        xlsx_dicts = read_xlsx.to_dict("records")
        log(log.INFO, "Get xlsx text Canadian Pacific")

        data_dicts = []

        for i_dict in xlsx_dicts:
            for i, value in i_dict.items():
                if re.search(r"\bcarloads\b", str(value).lower()):
                    index = xlsx_dicts.index(i_dict)
                    year = re.findall(r"(\d+)", value)
                    data_dicts = xlsx_dicts[index + 2:]
                    d_dicts = data_dicts[2:]
                    products = {}
                    for d in d_dicts:
                        data = {}
                        data_arr = []
                        data_arr.append(data)
                        weeks = data_dicts[0]
                        times = data_dicts[1]
                        for i, week in weeks.items():
                            if str(week) != "nan" and type(week) != str:
                                for j, num in d.items():
                                    if (
                                        str(num) != "nan"
                                        and type(num) != str
                                        and i == j
                                    ):
                                        for k, data_time in times.items():
                                            if (
                                                str(data_time) != "nan"
                                                and type(data_time) != str
                                                and i == j == k
                                            ):
                                                data[str(week)] = {
                                                    "num": str(num),
                                                    "time": str(data_time),
                                                }
                        products[d["Unnamed: 1"]] = data

                    # write data to the database
                    for prod_name in products:
                        product = products[prod_name]
                        company_id = ""
                        carload_id = find_carload_id(prod_name)
                        for week_number, carload_number in product.items():
                            company_id = (
                                f"Canadian_Pacific_{year[0]}_{week_number}_{carload_id}"
                            )
                            company = Company.query.filter(
                                and_(
                                    Company.company_id == company_id,
                                    Company.product_type == prod_name,
                                )
                            ).first()
                            data = carload_number["time"].split(" ")[0].split("-")
                            if not company and carload_id is not None:
                                Company(
                                    company_id=company_id,
                                    carloads=int(carload_number["num"]),
                                    date=date(int(data[0]), int(data[1]), int(data[2])),
                                    week=int(week_number),
                                    year=int(year[0]),
                                    company_name="Canadian Pacific",
                                    carload_id=carload_id,
                                    product_type=prod_name,
                                ).save()
                        log(log.INFO, "Write data to the database Canadian Pacific")
