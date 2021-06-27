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
        if self.year_no != 2021:
            if len(str(self.week_no)) == 1:
                week = f"0{self.week_no}"
            else:
                week = self.week_no
        else:
            week = self.week_no
        if self.year_no == 2020 and 14 < self.week_no < 22:
            week = "%20" + str(week)
        file_url = f"https://www.cn.ca/-/media/Files/Investors/Investor-Performance-Measures/{self.year_no}/Week{week}.xlsx"  # noqa E501
        file = urlopen(file_url)
        if file.url == "https://www.cn.ca/404":
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
        log(log.INFO, "Read xlsx file Canadian National")
        read_xlsx = pd.read_excel(file_xlsx, header=None)
        xlsx_dicts = read_xlsx.to_dict("records")
        log(log.INFO, "Get xlsx text Canadian National")

        data_dicts = []

        xlsx_date = xlsx_dicts.pop(2)[0].replace("-", "")

        dates = search_dates(xlsx_date)
        date = []

        for x in dates[0]:
            date.append(x)

        date = date[1]

        for xlsx_dict in xlsx_dicts:
            type_name = xlsx_dict[0]
            if type_name and type_name in [
                "Other Carloads",
                "Automotive",
                "Food & Kindred Products",
            ]:
                data_dicts.append(xlsx_dict)

        for xlsx_dict in xlsx_dicts:
            type_name = xlsx_dict[1]
            if type_name and type_name in ALL_PROD_TYPES:
                data_dicts.append(xlsx_dict)

        data_products = []
        for data_dict in data_dicts:
            data_product = {}
            for ind in data_dict:
                d = data_dict[ind]
                if str(d) != "nan":
                    dic = {ind: d}
                    data_product.update(dic)
            data_products.append(data_product)

            d_products = []
            for data in data_products:
                d_product = {}
                count = 0
                for i, val in data.items():
                    d = {count: val}
                    count += 1
                    d_product.update(d)
                d_products.append(d_product)

        products = {}

        for data in d_products:
            products[data[0]] = dict(
                week=dict(
                    current_year=data[1],
                    previous_year=data[2],
                    chg=round(data[4] * 100, 1),
                ),
                QUARTER_TO_DATE=dict(
                    current_year=data[5],
                    previous_year=data[6],
                    chg=round(data[8] * 100, 1),
                ),
                YEAR_TO_DATE=dict(
                    current_year=data[9],
                    previous_year=data[10],
                    chg=round(data[12] * 100, 1),
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
                    carload_id=carload_id,
                    product_type=prod_name,
                ).save()
        log(log.INFO, "Write data to the database Canadian National")
