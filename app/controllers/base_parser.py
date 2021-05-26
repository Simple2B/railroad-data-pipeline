from PyPDF2 import PdfFileReader

class BaseParser:
    def __init__(self):
        pass

    def get_file(self) -> bool:
        raise NotImplementedError()

    def parse_data(self, file=None):
        raise NotImplementedError()

    def get_pdf_text(self, file):
        pdf = PdfFileReader(file)
        text = ""
        for i in range(pdf.getNumPages()):
            page = pdf.getPage(i)
            text += page.extractText()
        if text:
            text = " ".join(text.split("\n"))
        return text


def get_int_val(val: str) -> int:
    return int(val.replace(",", ""))
