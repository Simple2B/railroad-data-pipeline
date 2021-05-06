from urllib.request import urlopen
from .base_parser import BaseParser
import PyPDF2
from .scrapper import scrapper
from app.logger import log

# import re


class CSXParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "https://investors.csx.com/metrics/default.aspx"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream

    def get_file(self) -> bool:
        file_url = scrapper('csx', self.week_no, self.year_no, self.URL)
        file = urlopen(file_url)
        if file:
            self.file = file
            return True
        log(log.ERROR, "File not found")
        return False

    def parse_data(self, file=None):
        if not file:
            file = self.file
        # with open(file, "rb") as pdfFile:
        pdfReader = PyPDF2.PdfFileReader(file)
        pages = pdfReader.numPages
        pages

        pg = pdfReader.getPage(0)
        #print(pg)
        textPdf = pg.extractText()
        textPdf

        # pages = pdfReader.getNumPages()

        # body_text = ''

        # for p in pages:
        #     page = pdfReader.getPage(p)
        #     text = page.extractText

        #     rex = re.compile("(?<=\%\%\(S\$\))(.*)", re.DOTALL)
        #     body_text = re.search(rex, text).group(0)
        #     body_text

            # titles = re.findall(r'([a-zA-Z\s])(?=\n)', body)

            # for title in titles:
