from monopoly.pdf import PDF
import os


class OCBC(PDF):
    def __init__(self, file_path: str):
        super().__init__(file_path)

        self.password = os.environ["OCBC_PDF_PASSWORD"]
        self.regex_pattern = r"(\d+\/\d+)(.*?)([\d.,]+)$"
