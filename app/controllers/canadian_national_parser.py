import re
from datetime import datetime
import tempfile
import pandas as pd
from sqlalchemy import and_
from urllib.request import urlopen
from .base_parser import BaseParser
from .carload_types import find_carload_id
from app.logger import log
from app.models import Company


class CanadianNationalParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "https://www.cn.ca/en/investors/key-weekly-metrics/"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream

    def get_file(self) -> bool:
        if len(str(self.week_no)) == 1:
            week = f"0{self.week_no}"
        else:
            week = self.week_no
        file_url = f"https://www.cn.ca/-/media/Files/Investors/Investor-Performance-Measures/{self.year_no}/Week{int(week) - 1}.xlsx"  # noqa E501
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

        # Load spreadsheet
        file_xlsx = pd.ExcelFile(file)
        read_xlsx = pd.read_excel(file_xlsx, header=None)
        xlsx_dicts = read_xlsx.to_dict(orient="dictionary_xlsx")

        # xlsx_dicts = read_xlsx.to_dict('dictionary_xlsx')
        del xlsx_dicts[0]

        # get the date of report from the general dict
        months = {}
        for i, month in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")):
            months[month] = i + 1

        date = xlsx_dicts[2][10].split(" ")

        day = date[6]
        year = date[7]
        month = date[3]
        format_month = months[month]

        format_day = int(re.findall(r"(\d+)", day)[0])
        format_year = int(re.findall(r"(\d+)", year)[0])

        format_date = datetime(month=format_month, day=format_day, year=format_year)
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
                    date=format_date,
                    week=self.week_no,
                    year=self.year_no,
                    company_name="Canadian National",
                    product_type=prod_name,
                ).save()
