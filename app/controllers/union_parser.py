import re
from datetime import datetime
import datefinder
import requests
from .base_parser import BaseParser, get_int_val
from pdfreader import SimplePDFViewer
from .scrapper import scrapper
from .carload_types import find_carload_id
from app.logger import log
from app.models import Company
from sqlalchemy import and_


class UnionParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "https://www.up.com/investor/aar-stb_reports/2021_Carloads/index.htm"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream

    def get_file(self) -> bool:
        file_url = scrapper('union', self.week_no, self.year_no, self.URL)
        requests.packages.urllib3.disable_warnings()
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        file = requests.get(file_url, stream=True)
        if file:
            self.file = file.content
            return True
        log(log.ERROR, "File not found")
        return False

    def parse_data(self, file=None):
        if not file:
            file = self.file
        viewer = SimplePDFViewer(file)
        text_pdf = ""
        for canvas in viewer:
            text_pdf += " ".join(canvas.strings)

        matches = datefinder.find_dates(text_pdf)

        COUNT_FIND_DATE = 2
        date = datetime.now()
        for i, match in enumerate(matches):
            date = match
            if i >= COUNT_FIND_DATE:
                break

        last_skip_word = "% Chg"
        skip_index = text_pdf.rindex(last_skip_word) + len(last_skip_word)
        text_pdf = text_pdf[skip_index:].strip()
        PATTERN = (
            r"(?P<name>[a-zA-Z0-9_\ \(\)\.\&\,\-]+)\s+"
            r"(?P<w_current_year>[0-9\,]+)\s+"
            r"(?P<w_previous_year>[0-9\,]+)\s+"
            r"(?P<w_chg>[0-9\.\%\-\(\)]+)\s+"
            r"(?P<q_current_year>[0-9\,]+)\s+"
            r"(?P<q_previous_year>[0-9\,]+)\s+"
            r"(?P<q_chg>[0-9\.\%\-\(\)]+)\s+"
            r"(?P<y_current_year>[0-9\,]+)\s+"
            r"(?P<y_previous_year>[0-9\,]+)\s+"
            r"(?P<y_chg>[0-9\.\%\-\(\)]+)"
        )

        # list of all products
        products = {}
        for line in re.finditer(PATTERN, text_pdf):
            products[line["name"].strip()] = dict(
                week=dict(
                    current_year=get_int_val(line["w_current_year"]),
                    previous_year=get_int_val(line["w_previous_year"]),
                    chg=line["w_chg"],
                ),
                QUARTER_TO_DATE=dict(
                    current_year=get_int_val(line["q_current_year"]),
                    previous_year=get_int_val(line["q_previous_year"]),
                    chg=line["q_chg"],
                ),
                YEAR_TO_DATE=dict(
                    current_year=get_int_val(line["y_current_year"]),
                    previous_year=get_int_val(line["y_previous_year"]),
                    chg=line["y_chg"],
                ),
            )

        for prod_name in products:
            company_id = ""
            carload_id = find_carload_id(prod_name)
            company_id = f"Union_Pacific_{self.year_no}_{self.week_no}_{carload_id}"
            company = Company.query.filter(
                and_(
                    Company.company_id == company_id, Company.product_type == prod_name
                )
            ).first()
            if not company and carload_id is not None:
                Company(
                    company_id=company_id,
                    carloads=products[prod_name]["week"]["current_year"],
                    YOYCarloads=products[prod_name]["week"]["current_year"]
                    - products[prod_name]["week"]["previous_year"],
                    QTDCarloads=products[prod_name]["QUARTER_TO_DATE"]["current_year"],
                    YOYQTDCarloads=products[prod_name]["QUARTER_TO_DATE"][
                        "current_year"
                    ]
                    - products[prod_name]["QUARTER_TO_DATE"]["previous_year"],
                    YTDCarloads=products[prod_name]["YEAR_TO_DATE"]["current_year"],
                    YOYYDCarloads=products[prod_name]["YEAR_TO_DATE"]["current_year"]
                    - products[prod_name]["YEAR_TO_DATE"]["previous_year"],
                    date=date,
                    week=self.week_no,
                    year=self.year_no,
                    company_name="UNION",
                    product_type=prod_name,
                ).save()
