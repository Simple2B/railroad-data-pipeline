import re
import tempfile
import datefinder
import requests
from datetime import datetime
from pdfreader import SimplePDFViewer
# import PyPDF2
# from urllib.request import urlopen
from sqlalchemy import and_
from .scrapper import scrapper
from .carload_types import find_carload_id
from .base_parser import BaseParser
# from app.logger import log
from app.models import Company


class CSXParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "https://investors.csx.com/metrics/default.aspx"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream

    def get_file(self) -> bool:
        file_url = scrapper("csx", self.week_no, self.year_no, self.URL)
        file = requests.get(file_url, stream=True)
        file.raise_for_status()
        self.file = tempfile.NamedTemporaryFile(mode="wb+")
        for chunk in file.iter_content(chunk_size=4096):
            self.file.write(chunk)
        self.file.seek(0)
        return True

    def parse_data(self, file=None):
        if not file:
            file = self.file

        pdf_text = ""
        # reads each of the pdf pages

        viewer = SimplePDFViewer(file)
        for canvas in viewer:
            pdf_text += " ".join(canvas.strings)

        matches = datefinder.find_dates(pdf_text)

        COUNT_FIND_DATE = 2
        date = datetime.now()
        for i, match in enumerate(matches):
            date = match
            if i >= COUNT_FIND_DATE:
                break

        date

        last_skip_word = "% Chg"

        skip_index = pdf_text.rindex(last_skip_word) + len(last_skip_word)
        pdf_text = pdf_text[skip_index:].strip()

        PATTERN = (
            r"(?P<name>[a-zA-Z0-9_\ \(\)\.\&\,\-]+)\s+"
            r"(?P<w_current_year>[0-9\,]+)\s+"
            r"(?P<w_previous_year>[0-9\,]+)\s+"
            r"(?P<w_chg>[0-9\.\%\-]+)\s+"
            r"(?P<q_current_year>[0-9\,]+)\s+"
            r"(?P<q_previous_year>[0-9\,]+)\s+"
            r"(?P<q_chg>[0-9\.\%\-]+)\s+"
            r"(?P<y_current_year>[0-9\,]+)\s+"
            r"(?P<y_previous_year>[0-9\,]+)\s+"
            r"(?P<y_chg>[0-9\.\%\-]+)"
        )

        # get the date of report from the general text
        
        matches = datefinder.find_dates(format_text)

        month = ""
        day = ""
        year = ""

        for match in matches:
            month = match.month
            day = match.day
            year = match.year

        date = datetime(month=month, day=day, year=year)

        # list of all products
        products = {}

        def get_int_val(val: str) -> int:
            return int(val.replace(",", ""))

        for line in re.finditer(PATTERN, format_text):
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

        # write data to the database
        for prod_name, product in products.items():
            carload_id = find_carload_id(prod_name)
            company_id = f"CSX_{self.year_no}_{self.week_no}_{carload_id}"

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
                    YOYQTDCarloads=product["QUARTER_TO_DATE"][
                        "current_year"
                    ]
                    - products[prod_name]["QUARTER_TO_DATE"]["previous_year"],
                    YTDCarloads=products[prod_name]["YEAR_TO_DATE"]["current_year"],
                    YOYYDCarloads=products[prod_name]["YEAR_TO_DATE"]["current_year"]
                    - products[prod_name]["YEAR_TO_DATE"]["previous_year"],
                    date=date,
                    week=self.week_no,
                    year=self.year_no,
                    company_name="CSX",
                    product_type=prod_name,
                ).save()
