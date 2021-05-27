# import re
# from datetime import datetime
from dateparser.search import search_dates
import tempfile
import pandas as pd
from sqlalchemy import and_
from urllib.request import urlopen
from .base_parser import BaseParser
from app.logger import log
from .carload_types import find_carload_id, ALL_PROD_TYPES
from app.models import Company


class CanadianNationalParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "https://www.cn.ca/en/investors/key-weekly-metrics/"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream

    def get_file(self) -> bool:
        # if len(str(self.week_no)) == 1:
        #     week = f"0{self.week_no}"
        # else:
        #     week = self.week_no
        file_url = f"https://www.cn.ca/-/media/Files/Investors/Investor-Performance-Measures/{self.year_no}/Week{int(self.week_no) - 1}.xlsx"  # noqa E501
        file = urlopen(file_url)
        if file.url == 'https://www.cn.ca/404':
            log(log.ERROR, "File is not found.")
            return None
        log(log.INFO, "Found pdf link: [%s]", file_url)
        self.file = tempfile.NamedTemporaryFile(mode="wb+")
        for line in file.readlines():
            self.file.write(line)
        self.file.seek(0)
        return True

    def parse_data(self, file=None):
        if not file:
            file = self.file

        # if not self.file:
        #     log(log.ERROR, "Nothing to parse, file is not found")
        #     return None

        # Load spreadsheet
        file_xlsx = pd.ExcelFile(file)
        read_xlsx = pd.read_excel(file_xlsx, header=None)
        xlsx_dicts = read_xlsx.to_dict("records")

        data_dicts = []

        xlsx_date = xlsx_dicts.pop(2)[0].replace("-", "")

        dates = search_dates(xlsx_date)
        date = []

        for x in dates[0]:
            date.append(x)

        date = date[1]

        for xlsx_dict in xlsx_dicts:
            type_name = xlsx_dict[1]
            if type_name and type_name in ALL_PROD_TYPES:
                data_dicts.append(xlsx_dict)

        products = {}

        for data in data_dicts:
            products[data[1]] = dict(
                week=dict(
                    current_year=data[2],
                    previous_year=data[3],
                    chg=round(data[5] * 100, 1),
                ),
                QUARTER_TO_DATE=dict(
                    current_year=data[7],
                    previous_year=data[8],
                    chg=round(data[10] * 100, 1),
                ),
                YEAR_TO_DATE=dict(
                    current_year=data[12],
                    previous_year=data[13],
                    chg=round(data[15] * 100, 1),
                ),
            )

        # write data to the database
        for prod_name, product in products.items():
            company_id = ""
            carload_id = find_carload_id(prod_name)
            company_id = f"Canadian_National_{self.year_no}_{self.week_no}_{carload_id}"
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
                    company_name="Canadian National",
                    product_type=prod_name,
                ).save()
