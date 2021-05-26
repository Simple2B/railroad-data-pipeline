import re
from PyPDF2 import PdfFileReader
from pdfreader import SimplePDFViewer


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
        return text.strip()

    def get_simple_pdf_text(self, file):
        pdf_text = ""
        viewer = SimplePDFViewer(file)
        viewer.render()
        for canvas in viewer:
            pdf_text += "".join(canvas.strings)

        if not pdf_text.strip():
            return ""

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

        return re.sub(r'\s+', ' ', pdf_text).strip()


def get_int_val(val: str) -> int:
    return int(val.replace(",", ""))
