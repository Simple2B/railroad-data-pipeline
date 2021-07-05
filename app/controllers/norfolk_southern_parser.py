import re
from datetime import datetime

# import parser object from tike
# from tika import parser

# import datefinder
import tempfile
import PyPDF2

from pdfrw import PdfReader

# import unicode
# import gzip

# import pdfrw

from bs4 import BeautifulSoup
from selenium import webdriver
from isoweek import Week
from config import BaseConfig as conf
from app.logger import log
from urllib.request import urlopen
from sqlalchemy import and_
from .base_parser import BaseParser
from .carload_types import find_carload_id
from app.models import Company


class NorfolkSouthernParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "http://www.nscorp.com/content/nscorp/en/investor-relations/performance-metrics.html"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream
        self.link = None

    def scrapper(self) -> str or None:
        date = Week(self.year_no, self.week_no)
        month = date.day(0).month
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        browser = webdriver.Chrome(
            options=options, executable_path=conf.CHROME_DRIVER_PATH
        )
        log(log.INFO, "Start get url Norfolk Southern")
        browser.get(self.URL)
        log(log.INFO, "Get url Norfolk Southern")
        generated_html = browser.page_source
        soup = BeautifulSoup(generated_html, "html.parser")
        tags = soup.find_all("a")
        log(log.INFO, "Get all links Norfolk Southern")
        link = [
            link.attrs["href"]
            for link in tags
            if f"weekly-performance-reports/{self.year_no}/investor-weekly-carloads"
            in link.attrs["href"]
        ]
        if not link:
            log(log.WARNING, "Links not found")
            return None
        log(log.INFO, "Get link with pdf for Norfolk Southern")
        link = "http://www.nscorp.com" + link[month - 1]
        log(log.INFO, "Found pdf link: [%s]", link)
        return link

    def get_file(self) -> bool:
        file_url = self.scrapper()
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

        # the first method of parsing

        doc = PdfReader(file.name)
        for page in doc.pages:
            bytestream = page.Contents.stream

            d = bytestream.encode("utf-8")
            d

        # the second method of parsing

        pdf_text = ""
        # reads each of the pdf pages
        pages_text = []
        pdf_reader = PyPDF2.PdfFileReader(file)
        log(log.INFO, "Read pdf file Norfolk Southern")
        for page_number in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_number)
            if page:
                pdf_text = page.extractText()
                pages_text.append(pdf_text)

        log(log.INFO, "Get pdf text Norfolk Southern")
        all_text = []

        # format text on all pages
        for text in pages_text:
            # format_text = re.sub("\n", " ", text)
            format_text = text.split()
            all_text.append(format_text)

        # format_all_text_date = []
        format_all_text = []

        for text in all_text:
            for key in text:
                world_index = text.index("Norfolk")
                if key == "Norfolk":
                    # format_text_date = " ".join(text[:world_index])
                    # format_text_date
                    # format_all_text_date.append(format_text_date)
                    format_text = " ".join(text[world_index:])
                    format_text = format_text.replace("(", " ").replace(")", " ")
                    format_text = re.sub(r"\s+", " ", format_text)
                    format_text = re.sub(r"(\-)\s+(\d)", r"\1\2", format_text)
                    format_all_text.append(format_text)

        find_worlds = []

        PATTERN_WORLD = r"(?P<name>[a-zA-Z\)\ ]+)"

        log(log.INFO, "Start find worlds like PATTERN_WORLD Norfolk Southern")

        for pdf_text in format_all_text:
            for t in re.finditer(PATTERN_WORLD, pdf_text):
                find_worlds.append(t["name"])

        log(log.INFO, "End find worlds like PATTERN_WORLD Norfolk Southern")

        find_worlds = [x.strip() for x in find_worlds if x.strip()]

        log(log.INFO, "Start add space Norfolk Southern")

        format_text = []

        for pdf_text in format_all_text:
            for word in find_worlds:
                pdf_text = pdf_text.replace(word, f" {word} ")
                pdf_text = re.sub(r"\s+", " ", pdf_text)

            format_text.append(pdf_text)

        log(log.INFO, "End add space Norfolk Southern")

        format_all_text_date = {}

        pattern_week1 = r"((Week\b)\ [0-9][0-9])"
        pattern_week2 = r"((Week[0-9]\b))"
        pattern_week3 = r"((Week[0-9][0-9]\b))"
        pattern_week4 = r"((Week [0-9]\b))"

        for data in format_text:
            data = data.strip()
            found_1_week = re.findall(pattern_week1, data)
            found_2_week = re.findall(pattern_week2, data)
            found_3_week = re.findall(pattern_week3, data)
            found_4_week = re.findall(pattern_week4, data)

            if found_1_week != []:
                week_1 = int("".join(i for i in found_1_week[0][0] if i.isdigit()))
                format_all_text_date[week_1] = data
            if found_2_week != []:
                week_2 = int("".join(i for i in found_2_week[0][0] if i.isdigit()))
                format_all_text_date[week_2] = data
            if found_3_week != []:
                week_3 = int("".join(i for i in found_3_week[0][0] if i.isdigit()))
                format_all_text_date[week_3] = data
            if found_4_week != []:
                week_4 = int("".join(i for i in found_4_week[0][0] if i.isdigit()))
                format_all_text_date[week_4] = data

        # del format_all_text_date[next(iter(format_all_text_date))]

        pattern_date1 = r"(To: ([0-9][0-9] -[0-9][0-9] -[0-9][0-9][0-9][0-9]))"
        pattern_date2 = r"(To : ([0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]))"
        p_date1 = r"([0-9][0-9] -[0-9][0-9] -[0-9][0-9][0-9][0-9])"

        for index, text in format_all_text_date.items():
            word = "Chg"
            text = text.replace(word, "")
            text = re.sub(r"\s+", " ", text)
            if re.findall(pattern_date1, text):
                date = re.findall(pattern_date1, text)
                date = re.findall(p_date1, date[0][0])
                date = date[0].replace(" ", "")
                date = datetime.strptime(date, "%m-%d-%Y")
            if re.findall(pattern_date2, text):
                date = re.findall(pattern_date2, text)
                date = date[0][1]
                date = datetime.strptime(date, "%m-%d-%Y")
            format_all_text_date[index] = dict(text=text, date=date)

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
        # PATTERN_DATE = (
        #     r"Week\s+"
        #     r"(?P<week>\d+)\s+"
        #     r"\(Q\d\)\s+From:\s+"
        #     r"\d+\s+\d+\s+\d+\s+To:\s+"
        #     r"(?P<month>\d+)\s+"
        #     r"(?P<day>\d+)\s+"
        #     r"(?P<year>\d+)\s"
        # )

        # list of all products_date
        # all_date = []
        # dates = {}

        # for date in format_all_date:
        #     for line in re.finditer(PATTERN_DATE, date):
        #         dates = dict(
        #             week_num=line["week"],
        #             month_num=line["month"],
        #             day_num=line["day"],
        #             year_num=line["year"],
        #         )
        #         all_date.append(dates)

        # list of all products
        # format_all_text_date
        # all_pages_products = []
        products = {}

        def get_int_val(val: str) -> int:
            result = None
            if val.count(","):
                result = int(val.replace(",", ""))
            elif val.count("."):
                result = int(val.replace(".", ""))
            elif val:
                result = int(val)
            if result:
                return result
            return 0

        for ind_week, val_text_date in format_all_text_date.items():
            ind_week
            val_text_date
            if ind_week == self.week_no:
                week = ind_week
                text_date = val_text_date["text"]
                date = val_text_date["date"]
                for line in re.finditer(PATTERN_TEXT, text_date):
                    products[line["name"].strip()] = dict(
                        week=dict(
                            current_year=get_int_val(line["w_current_year"]),
                            previous_year=get_int_val(line["w_previous_year"]),
                            chg=get_int_val(line["w_chg"]),
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
                            week_num=week,
                            date=date,
                        ),
                    )
        products
        # write data to the database
        for prod, prod_data in products.items():
            company_id = ""
            carload_id = find_carload_id(prod)
            prod_week = prod_data["date"]["week_num"]
            prod_date = prod_data["date"]["date"]

            company_id = f"Norfolk_Southern_{self.year_no}_{prod_week}_{carload_id}"
            company = Company.query.filter(
                and_(
                    Company.company_id == company_id,
                    Company.product_type == prod,
                )
            ).first()
            if not company and carload_id is not None:
                Company(
                    company_id=company_id,
                    carloads=prod_data["week"]["current_year"],
                    YOYCarloads=prod_data["week"]["current_year"]
                    - prod_data["week"]["previous_year"],
                    QTDCarloads=prod_data["QUARTER_TO_DATE"]["current_year"],
                    YOYQTDCarloads=prod_data["QUARTER_TO_DATE"]["current_year"]
                    - prod_data["QUARTER_TO_DATE"]["previous_year"],
                    YTDCarloads=prod_data["YEAR_TO_DATE"]["current_year"],
                    YOYYDCarloads=prod_data["YEAR_TO_DATE"]["current_year"]
                    - prod_data["YEAR_TO_DATE"]["previous_year"],
                    date=prod_date,
                    week=prod_week,
                    year=self.year_no,
                    company_name="Nortfolk Southern",
                    carload_id=carload_id,
                    product_type=prod,
                ).save()
        log(log.INFO, "Write data to the database Norfolk Southern")
