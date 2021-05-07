import re
from urllib.request import urlopen
from .base_parser import BaseParser
import PyPDF2
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
        pdf_reader = PyPDF2.PdfFileReader(file)
        for page_number in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_number)
            pdf_text = page.extractText()

        format_text = re.sub("\n", " ", pdf_text)
        text_elem = format_text.split()[12:]

        def format_list_product(product):
            list2=[]
            list3=[]
            for i in product:
                if re.search("\d", i):
                    list3.append(i)
                else:
                    list2.append(i)
            answer = []
            answer.append(' '.join(list2))
            answer.extend(list3)
            return answer

        list_products_data = []

        def create_data_csx(product):
            dict_product = {}
            dict_product['product_name'] = product[0]
            dict_product['week'] = {}
            dict_product['week']['current_year'] = product[1]
            dict_product['week']['previous_year'] = product[2]
            dict_product['week']['сhg'] = product[3]

            dict_product['QUARTER_TO_DATE'] = {}
            dict_product['QUARTER_TO_DATE']['current_year'] = product[4]
            dict_product['QUARTER_TO_DATE']['previous_year'] = product[5]
            dict_product['QUARTER_TO_DATE']['сhg'] = product[6]

            dict_product['YEAR_TO_DATE'] = {}
            dict_product['YEAR_TO_DATE']['current_year'] = product[7]
            dict_product['YEAR_TO_DATE']['previous_year'] = product[8]
            dict_product['YEAR_TO_DATE']['сhg'] = product[9]

            return list_products_data.append(dict_product)


        product_crain = text_elem[:10]
        product_crain_mill = format_list_product(text_elem[10:22])
        product_farm = format_list_product(text_elem[22:35])
        product_food = format_list_product(text_elem[35:46])
        product_chemicals = text_elem[46:56]

        product_petroleum = format_list_product(text_elem[56:69])
        product_primary_metal = format_list_product(text_elem[69:81])
        product_primary_forest = format_list_product(text_elem[81:93])
        product_lumber = format_list_product(text_elem[93:106])
        product_pulp = format_list_product(text_elem[106:119])
        product_non_metallic_minerals = format_list_product(text_elem[119:132])
        product_crushed_gravel = format_list_product(text_elem[132:146])
        product_stone_clay_glass = format_list_product(text_elem[146:160])
        product_iron_steel = format_list_product(text_elem[160:173])
        product_waste = format_list_product(text_elem[173:186])
        product_motor = format_list_product(text_elem[186:199])
        product_metallic = format_list_product(text_elem[199:210])
        product_coal = text_elem[210:220]
        product_coke = text_elem[220:230]

        product_all_other_carloads = format_list_product(text_elem[230:242])
        product_total_carloads = format_list_product(text_elem[242:253])
        product_trailers = format_list_product(text_elem[253:263])
        product_containers = format_list_product(text_elem[263:273])
        product_total_intermodal = format_list_product(text_elem[273:284])
        product_total_traffic = format_list_product(text_elem[284:295])

        list_products = [
            product_crain,
            product_crain_mill,
            product_farm,
            product_food,
            product_chemicals,
            product_petroleum,
            product_primary_metal,
            product_primary_forest,
            product_lumber,
            product_pulp,
            product_non_metallic_minerals,
            product_crushed_gravel,
            product_stone_clay_glass,
            product_iron_steel,
            product_waste,
            product_motor,
            product_metallic,
            product_coal,
            product_coke,
            product_all_other_carloads,
            product_total_carloads,
            product_trailers,
            product_containers,
            product_total_intermodal,
            product_total_traffic,
        ]

        def add_data_products(list_products):
            for product in list_products:
                create_data_csx(product)

        add_data_products(list_products)

        return list_products_data
