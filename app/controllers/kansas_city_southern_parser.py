import re
import datefinder
from sqlalchemy import and_
from datetime import datetime
import PyPDF2
from urllib.request import urlopen
from .scrapper import scrapper
from .carload_types import CARLOAD_TYPES
from .base_parser import BaseParser
from app.logger import log
from app.models import Company


class KansasCitySouthernParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "https://investors.kcsouthern.com/performance-metrics/aar-weekly-carload-report/2021?sc_lang=e"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream

    def get_file(self) -> bool:
        file_url = scrapper(
            "kansas_city_southern", self.week_no, self.year_no, self.URL
        )
        file = urlopen(file_url)
        if file:
            self.file = file
            return True
        log(log.ERROR, "File not found")
        return False

    def parse_data(self, file=None):
        if not file:
            file = self.file

        pdf_text = ""
        # reads each of the pdf pages
        pdf_reader = PyPDF2.PdfFileReader(file)
        for page_number in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_number)
            pdf_text += page.extractText()

        # remove spaces from the text that we read from the pdf file
        format_text = re.sub("\n", " ", pdf_text)

        # the text of which we have a string we make an array of values from it
        format_text = " ".join(format_text.split()[12:])

        PATERN = (
            r"(?P<name>[a-zA-Z\ \(\)\.\&\,\-]+)\s+"
            r"(?P<KCSR>[0-9\,]+)\s+"
            r"(?P<KCSM>[0-9\,]+)\s+"
            r"(?P<Consolidated>[0-9\,]+)\s+"
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

        for line in re.finditer(PATERN, format_text):
            products[line["name"]] = dict(
                KCSR=get_int_val(line["KCSR"]),
                KCSM=get_int_val(line["KCSM"]),
                Consolidated=get_int_val(line["Consolidated"]),
            )

        # write data to the database
        for prod_name in products:
            company_id = ""
            for carload in CARLOAD_TYPES:
                if prod_name.lower() == carload["type"].lower():
                    company_id = (
                        f"Kansas_City_Southern_{self.year_no}_{self.week_no}_{carload['ID']}"
                    )
                    company = Company.query.filter(
                        and_(
                            Company.company_id == company_id,
                            Company.product_type == prod_name,
                        )
                    ).first()

                    if not company:
                        Company(
                            company_id=company_id,
                            carloads=products[prod_name]["Consolidated"],
                            YOYCarloads=None,
                            QTDCarloads=None,
                            YOYQTDCarloads=None,
                            YTDCarloads=None,
                            YOYYDCarloads=None,
                            date=date,
                            week=self.week_no,
                            year=self.year_no,
                            company_name="Kansas City Southern",
                            product_type=prod_name,
                        ).save()
