from .parser import BaseParser
import PyPDF2


class CSXParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "https://investors.csx.com/metrics/default.aspx"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream

    def get_file(self) -> bool:
        raise NotImplementedError()

    def parse_data(self, file=None):
        if not file:
            file = self.file
        plread = PyPDF2.PdfFileReader(file)
        plread
