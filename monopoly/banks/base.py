from monopoly.processor import StatementProcessor


class BankBase(StatementProcessor):
    """Helper class to handle initialization of common variables
    that are shared between bank classes"""

    def __init__(self, file_path: str, password: str = None):
        if password:
            # overwrite pydantic password with user-supplied password
            self.pdf_config.password = password

        super().__init__(
            statement_config=self.statement_config,
            pdf_config=self.pdf_config,
            file_path=file_path,
        )
