from urllib.request import urlopen
import PyPDF2
from .parser import BaseParser
from .scrapper import scrapper
from app.logger import log


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
        plread = PyPDF2.PdfFileReader(file)
        plread
