from monopoly.pdf import PDF


class OCBC(PDF):
    def __init__(self, file_path: str, password: str = ""):
        super().__init__(file_path)

        self.password = password
        self.regex_pattern = r"(\d+\/\d+)(.*?)([\d.,]+)$"
