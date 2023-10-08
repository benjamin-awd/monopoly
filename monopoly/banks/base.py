from monopoly.bank import Bank


class BankBase(Bank):
    """Helper class to handle initialization of common variables
    that are shared between bank classes"""

    def __init__(self, file_path: str):
        super().__init__(
            statement_config=self.statement_config,
            pdf_config=self.pdf_config,
            file_path=file_path,
        )
