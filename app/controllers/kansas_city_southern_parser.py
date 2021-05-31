import re
import datefinder
import tempfile
from urllib.request import urlopen
from sqlalchemy import and_
from datetime import datetime
import PyPDF2
from bs4 import BeautifulSoup
from selenium import webdriver
from config import BaseConfig as conf
from app.logger import log
from .carload_types import find_carload_id
from .base_parser import BaseParser
from app.models import Company


class KansasCitySouthernParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = f"https://investors.kcsouthern.com/performance-metrics/aar-weekly-carload-report/{year_no}?sc_lang=e"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream
        self.links = None

    def scrapper(self, week: int, year: int) -> str or None:
        links = self.links
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        browser = webdriver.Chrome(
            options=options, executable_path=conf.CHROME_DRIVER_PATH
        )
        log(log.INFO, "Start get url Kansas City")
        browser.get(self.URL)
        log(log.INFO, "Got url Kansas City")
        generated_html = browser.page_source
        soup = BeautifulSoup(generated_html, "html.parser")
        links = soup.find_all("a", class_="ext-link")
        for i in links:
            if len(str(week)) == 1:
                week = f"0{week}"
            scrap_data = i.attrs["href"].split("/")[6]
            scrap_date = scrap_data.split("-")
            scrap_week = scrap_date[1]
            scrap_year = scrap_date[4]
            if str(week) == scrap_week and str(year) == scrap_year:
                link = "https://investors.kcsouthern.com" + i.attrs["href"]
                log(log.INFO, "Found pdf link: [%s]", link)
                return link
        log(log.WARNING, "Links not found")
        return None

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

        pdf_text = ""
        # reads each of the pdf pages
        pdf_reader = PyPDF2.PdfFileReader(file)
        log(log.INFO, "--------Read pdf file Kansas City--------")
        for page_number in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_number)
            pdf_text += page.extractText()
        log(log.INFO, "--------Get pdf text Kansas City--------")

        # remove spaces from the text that we read from the pdf file
        format_text = re.sub("\n", " ", pdf_text)

        # the text of which we have a string we make an array of values from it
        format_text = " ".join(format_text.split()[12:])

        PATTERN = (
            r"(?P<name>[a-zA-Z\ \(\)\.\&\,\-]+)\s+"
            r"(?P<KCSR>[0-9\,]+)\s+"
            r"(?P<KCSM>[0-9\,]+)\s+"
            r"(?P<Consolidated>[0-9\,]+)\s+"
        )

        # get the date of report from the general text
        matches = datefinder.find_dates(format_text)
        date = datetime.now()
        for match in matches:
            date = match

        # list of all products
        products = {}

        def get_int_val(val: str) -> int:
            return int(val.replace(",", ""))

        for line in re.finditer(PATTERN, format_text):
            products[line["name"]] = dict(
                KCSR=get_int_val(line["KCSR"]),
                KCSM=get_int_val(line["KCSM"]),
                Consolidated=get_int_val(line["Consolidated"]),
            )

        # write data to the database
        for prod_name in products:
            company_id = ""
            carload_id = find_carload_id(prod_name)
            company_id = (
                f"Kansas_City_Southern_{self.year_no}_{self.week_no}_{carload_id}"
            )
            company = Company.query.filter(
                and_(
                    Company.company_id == company_id,
                    Company.product_type == prod_name,
                )
            ).first()

            if not company and carload_id is not None:
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
        log(
            log.INFO,
            "-------- Write data to the database Kansas City Southern --------",
        )
