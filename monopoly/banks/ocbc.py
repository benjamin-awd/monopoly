from monopoly.pdf import PDF


class OCBC(PDF):
    def __init__(self, file_path: str, password: str = ""):
        super().__init__(file_path)

        self.password = password
        self.regex_pattern = r"(\d+\/\d+)\s*(.*?)\s*([\d.,]+)$"

    def _extract_text_from_pdf(self):
        # Call the parent class method to get the raw data
        transactions = super()._extract_text_from_pdf()
        print("Inside child")
        return transactions
