from monopoly.processor import StatementProcessor


class BankBase(StatementProcessor):
    """Helper class to handle initialization of common variables
    that are shared between bank classes"""

    def __init__(self, file_path: str, password: str = None):
        if password:
            # overwrite pydantic password with user-supplied password
            self.pdf_config.password = password

        # optional config
        brute_force_config = getattr(self, "brute_force_config", None)

        super().__init__(
            statement_config=self.statement_config,
            brute_force_config=brute_force_config,
            pdf_config=self.pdf_config,
            file_path=file_path,
        )
