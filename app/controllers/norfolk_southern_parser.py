import re
from datetime import datetime
import PyPDF2
from urllib.request import urlopen
from sqlalchemy import and_
from .scrapper import scrapper
from .base_parser import BaseParser
from app.logger import log
from app.models import Company


class NorfolkSouthernParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "http://www.nscorp.com/content/nscorp/en/investor-relations/performance-metrics.html"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream

    def get_file(self) -> bool:
        file_url = scrapper("norfolk_southern", self.week_no, self.year_no, self.URL)
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
        pages_text = []
        pdf_reader = PyPDF2.PdfFileReader(file)
        for page_number in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_number)
            pdf_text = page.extractText()
            pages_text.append(pdf_text)

        all_text = []

        # format text on all pages
        for text in pages_text:
            format_text = re.sub("\n", " ", text)
            format_text = format_text.split()
            all_text.append(format_text)

        all_text

        format_all_text_date = []
        format_all_text = []

        for text in all_text:
            for key in text:
                world_index = text.index('All')
                if key == 'All':
                    format_text_date = " ".join(text[:world_index])
                    format_all_text_date.append(format_text_date)
                    format_text = " ".join(text[world_index:])
                    format_text = format_text.replace("(", " ").replace(")", " ")
                    format_text = re.sub(r'\s+', ' ', format_text)
                    format_text = re.sub(r'(\-)\s+(\d)', r'\1\2', format_text)
                    format_all_text.append(format_text)

        format_all_date = []

        for text_date in format_all_text_date:
            text_date = text_date.replace("-", " ")
            text_date = re.sub("\n", " ", text_date)
            text_date = re.sub(r'\s+', ' ', text_date)
            text_date
            format_all_date.append(text_date)

        PATTERN_TEXT = (
            r"(?P<name>[a-zA-Z\ \.\&\,\ \*]+)\s+"
            r"(?P<w_current_year>[0-9\,\.\*]+)\s+"
            r"(?P<w_previous_year>[0-9\,\.\*]+)\s+"
            r"(?P<w_chg>[0-9\,\.\-]+)\s+"
            r"(?P<q_current_year>[0-9\,\.]+)\s+"
            r"(?P<q_previous_year>[0-9\,\.]+)\s+"
            r"(?P<q_chg>[0-9\,\.\-]+)\s+"
            r"(?P<y_current_year>[0-9\,\.]+)\s+"
            r"(?P<y_previous_year>[0-9\,\.]+)\s+"
            r"(?P<y_chg>[0-9\,\.\-]+)\s*"
        )

        # get the date of report from the general all_text
        PATTERN_DATE = (
            r"Week\s+"
            r"(?P<week>\d+)\s+"
            r"\(Q\d\)\s+From:\s+"
            r"\d+\s+\d+\s+\d+\s+To:\s+"
            r"(?P<month>\d+)\s+"
            r"(?P<day>\d+)\s+"
            r"(?P<year>\d+)\s"
        )

        # list of all products_date
        all_date = []
        dates = {}

        for date in format_all_date:
            for line in re.finditer(PATTERN_DATE, date):
                dates = dict(
                    week_num=line["week"],
                    month_num=line["month"],
                    day_num=line["day"],
                    year_num=line["year"],
                )
                all_date.append(dates)

        # list of all products
        all_pages_products = []
        products = {}

        def get_int_val(val: str) -> int:
            return int(val.replace(",", ""))

        for f_text in format_all_text:
            for line in re.finditer(PATTERN_TEXT, f_text):
                for date in all_date:
                    for d in date:
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
                            date=dict(
                                week_num=date["week_num"],
                                month_num=date["month_num"],
                                day_num=date["day_num"],
                                year_num=date["year_num"],
                            )
                        )
                all_pages_products.append(products)

        # write data to the database
        # for prod in all_pages_products:
            for prod in all_pages_products:
                for prod_name, product in prod.items():
                    company_id = f"Norfolk_Southern_{product['date']['year_num']}_{product['date']['week_num']}_XX"
                    date = datetime(month=int(product['date']['month_num']), day=int(product['date']
                                    ['day_num']), year=int(product['date']['year_num']))
                    company = Company.query.filter(
                        and_(
                            Company.company_id == company_id, Company.product_type == prod_name
                        )
                    ).first()
                    if not company:
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
                            week=int(product['date']['week_num']),
                            year=int(product['date']['year_num']),
                            company_name="Nortfolk Southern",
                            product_type=prod_name,
                        ).save()
