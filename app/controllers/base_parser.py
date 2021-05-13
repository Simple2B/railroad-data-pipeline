class BaseParser:
    def __init__(self):
        pass

    def get_file(self) -> bool:
        raise NotImplementedError()

    def parse_data(self, file=None):
        raise NotImplementedError()


def get_int_val(val: str) -> int:
    return int(val.replace(",", ""))
