import re
import tempfile
import datefinder
import requests
from datetime import datetime
import time
from pdfreader import SimplePDFViewer
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy import and_
from .carload_types import find_carload_id
from .base_parser import BaseParser
from app.logger import log
from config import BaseConfig as conf
from app.models import Company


class CSXParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "https://investors.csx.com/metrics/default.aspx"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None
        self.links = None

    def scrapper(self, week: int, year: int) -> str or None:
        links = self.links
        if not links:
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--headless")
            browser = webdriver.Chrome(options=options, executable_path=conf.CHROME_DRIVER_PATH)
            log(log.INFO, "Start get url CSX")
            browser.get(self.URL)
            log(log.INFO, "Got url CSX")
            generated_html = browser.page_source
            soup = BeautifulSoup(generated_html, "html.parser")
            links = soup.find_all("a", class_="module_link")
            while len(links) < 53:
                browser.get(self.URL)
                generated_html = browser.page_source
                soup = BeautifulSoup(generated_html, "html.parser")
                links = soup.find_all("a", class_="module_link")
                time.sleep(1)
            self.links = links
        for i in links:
            scrap_data = i.span.text.split()
            scrap_year = scrap_data[0]
            scrap_week = scrap_data[2]
            if scrap_year == str(year) and scrap_week == str(week):
                link = i["href"]
                log(log.INFO, "Found pdf link: [%s]", link)
                return link
        log(log.WARNING, "Links not found")
        return None

    def get_file(self) -> bool:
        file_url = self.scrapper(self.week_no, self.year_no)
        if not file_url:
            return False
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        self.file = tempfile.NamedTemporaryFile(mode="wb+", suffix=".pdf")
        for chunk in response.iter_content(chunk_size=4096):
            self.file.write(chunk)
        self.file.flush()
        self.file.seek(0)
        return True

    def parse_data(self, file=None):
        if not file:
            file = self.file

        pdf_text = self.get_pdf_text(file)
        # reads each of the pdf pages

        if not pdf_text:
            pdf_text = ""
            viewer = SimplePDFViewer(file)
            viewer.render()
            for canvas in viewer:
                pdf_text += "".join(canvas.strings)

        matches = datefinder.find_dates(pdf_text)

        COUNT_FIND_DATE = 2
        date = datetime.now()
        for i, match in enumerate(matches):
            date = match
            if i >= COUNT_FIND_DATE:
                break

        pdf_text = re.sub(r'\s+', ' ', pdf_text)
        pdf_text = pdf_text.replace('% Chg', ' % Chg ')
        pdf_text = pdf_text.split('% Chg')[-1].strip()
        pdf_text = pdf_text.replace('%', '% ')

        find_worlds = []

        PATTERN_WORLD = r"(?P<name>[a-zA-Z\(\)\&]+)"

        for t in re.finditer(PATTERN_WORLD, pdf_text):
            find_worlds.append(t["name"])

        for word in find_worlds:
            pdf_text = pdf_text.replace(word, f'{word} ')

        pdf_text = re.sub(r'\s+', ' ', pdf_text).strip()

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

        # list of all products
        products = {}

        def get_int_val(val: str) -> int:
            return int(val.replace(",", ""))

        for line in re.finditer(PATTERN, pdf_text):
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
