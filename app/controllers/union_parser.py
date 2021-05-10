import requests
from .base_parser import BaseParser
import PyPDF2
# import camelot
from .scrapper import scrapper
from app.logger import log


class UnionParser(BaseParser):
    def __init__(self, year_no: int, week_no: int):
        self.URL = "https://www.up.com/investor/aar-stb_reports/2021_Carloads/index.htm"
        self.week_no = week_no
        self.year_no = year_no
        self.file = None  # method get_file() store here file stream

    def get_file(self) -> bool:
        file_url = scrapper('union', self.week_no, self.year_no, self.URL)
        requests.packages.urllib3.disable_warnings()
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        file = requests.get(file_url, stream=True)
        if file:
            self.file = file.content
            return True
        log(log.ERROR, "File not found")
        return False

    def parse_data(self, file=None):
        if not file:
            file = self.file

        pdfReader = PyPDF2.PdfFileReader(file)
        pages = pdfReader.numPages
        pages

        pg = pdfReader.getPage(0)
        textPdf = pg.extractText()
        textPdf

        # df_list = []
        # results = camelot.read_pdf(file)
        # results
        # for table in results:
        #     t = table.parsing_report
        #     df_list.append(results[0].df)
