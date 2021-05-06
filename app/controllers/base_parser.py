class BaseParser:
    def __init__(self):
        pass

    def get_file(self) -> bool:
        raise NotImplementedError()

    def parse_data(self, file=None):
        raise NotImplementedError()
