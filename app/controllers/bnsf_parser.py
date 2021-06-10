import re
import tempfile
import datefinder
import requests
from sqlalchemy import and_
from datetime import datetime
import PyPDF2
from bs4 import BeautifulSoup
from selenium import webdriver
from config import BaseConfig as conf
from app.logger import log
from .base_parser import BaseParser
from .carload_types import find_carload_id
from app.models import Company


class BNSFParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "http://www.bnsf.com/about-bnsf/financial-information/index.html#Weekly+Carload+Reports"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream
        self.links = None

    def scrapper(self, week: int, year: int) -> str or None:
        if conf.CURRENT_WEEK > week and conf.CURRENT_YEAR > year:
            log(log.WARNING, "Links not found")
            return None
        links = self.links
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        browser = webdriver.Chrome(
            options=options, executable_path=conf.CHROME_DRIVER_PATH
        )
        log(log.INFO, "Start get url BNSF")
        browser.get(self.URL)
        log(log.INFO, "Got url BNSF")
        generated_html = browser.page_source
        soup = BeautifulSoup(generated_html, "html.parser")
        links = soup.find_all("a", class_="local-link")
        links_pdf = []
        for link in links:
            a = link.attrs["href"].split("/")[-1].split(".")[-1]
            text = link.text
            match = re.search(r"\d{2}\/\d{2}\/\d{4}", text)
            if a == "pdf" and match:
                links_pdf.append(link)
        for i in links_pdf:
            scrap_date = i.text.split("/")
            date = datetime(
                month=int(scrap_date[0]),
                day=int(scrap_date[1]),
                year=int(scrap_date[2]),
            )
            scrap_week = date.isocalendar()[1]
            if week == scrap_week and int(scrap_date[2]) == year:
                link = "http://www.bnsf.com" + i["href"]
                log(log.INFO, "Found pdf link: [%s]", link)
                return link

    def get_file(self) -> bool:
        file_url = self.scrapper(self.week_no, self.year_no)
        if not file_url:
            log(log.ERROR, "File URL is not found.")
            return False
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

        pdf_reader = PyPDF2.PdfFileReader(file)
        log(log.INFO, "Read pdf file BNSF")
        page = pdf_reader.getPage(0)
        pdf_text = page.extractText()
        log(log.INFO, "Get pdf text BNSF")

        # remove spaces from the text that we read from the pdf file
        format_text = re.sub("\n", " ", pdf_text)

        # remove characters
        format_text = format_text.replace("-", "").replace("|", "")

        # get the date of report from the general text
        matches = datefinder.find_dates(format_text)
        matches

        month = ""
        day = ""
        year = ""

        for match in matches:
            month = match.month
            day = match.day
            year = match.year

        date = datetime(month=month, day=day, year=year)

        # remove characters
        format_text = " ".join(format_text.split()[51:])
        format_text = format_text.replace("%", "")
        format_text = " ".join(format_text.split())

        PATTERN = (
            r"(?P<name>[(a-zA-Z)\ \(\)\.\&\,\-\/\ ]+)\s+"
            r"(?P<w_current_year>[(0-9)\,]+)\s+"
            r"(?P<q_current_year>[(0-9)\,]+)\s+"
            r"(?P<y_current_year>[(0-9)\.\,]+)\s+"
            r"(?P<w_previous_year>[(0-9)\.\,]+)\s+"
            r"(?P<q_previous_year>[(0-9)\,]+)\s+"
            r"(?P<y_previous_year>[(0-9)\.\,]+)\s+"
            r"(?P<w_chg>[(0-9)\.\ ]+)\s+"
            r"(?P<q_chg>[(0-9)\.\ ]+)\s+"
            r"(?P<y_chg>[(0-9)\ \.\ ]+)\s*"
        )

        # list of all products
        products = {}

        def get_int_val(val: str) -> int:
            result = None
            if val.count(","):
                result = int(val.replace(",", ""))
            elif val.count("."):
                result = int(val.replace(".", ""))
            if result:
                return result
            return 0

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
            company_id = ""
            carload_id = find_carload_id(prod_name)
            company_id = f"BNSF_{self.year_no}_{self.week_no}_{carload_id}"
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
                    YOYQTDCarloads=product["QUARTER_TO_DATE"]["current_year"]
                    - products[prod_name]["QUARTER_TO_DATE"]["previous_year"],
                    YTDCarloads=products[prod_name]["YEAR_TO_DATE"]["current_year"],
                    YOYYDCarloads=products[prod_name]["YEAR_TO_DATE"]["current_year"]
                    - products[prod_name]["YEAR_TO_DATE"]["previous_year"],
                    date=date,
                    week=self.week_no,
                    year=self.year_no,
                    company_name="BNSF",
                    carload_id=carload_id,
                    product_type=prod_name,
                ).save()
        log(log.INFO, "Write data to the database BNSF")
