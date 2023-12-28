import re
from functools import cached_property
from pathlib import Path
from typing import Any, Optional

from monopoly.config import CreditStatementConfig, DebitStatementConfig, PdfConfig
from monopoly.constants import AccountType, EncryptionIdentifier, MetadataIdentifier
from monopoly.pdf import PdfParser
from monopoly.processor import StatementProcessor


class ProcessorBase(StatementProcessor):
    """Helper class to handle initialization of common variables
    that are shared between bank processor classes"""

    # overwritten if pdf_config exists in bank class
    pdf_config: PdfConfig = PdfConfig()
    identifiers: list[EncryptionIdentifier | MetadataIdentifier]

    def __init__(
        self,
        file_path: Path,
        passwords: Optional[list[str]] = None,
    ):
        # this allows the user to override the default pydantic password
        # and supply their own password via the bank subclasses
        if passwords:
            self.pdf_config.passwords = passwords

        parser = PdfParser(file_path, self.pdf_config)

        self.pages = parser.get_pages()
        self.document = parser.document
        self.statement_type = self.get_statement_type()

        if isinstance(file_path, str):
            file_path = Path(file_path)

        super().__init__(
            parser=parser,
            file_path=file_path,
        )

    @cached_property
    def statement_config(self) -> CreditStatementConfig | DebitStatementConfig:
        if self.debit_header and self.debit_config:
            return self.debit_config
        return self.credit_config

    def get_statement_type(self) -> str:
        if not hasattr(self, "debit_config"):
            return AccountType.CREDIT
        if self.debit_header and self.debit_config:
            return AccountType.DEBIT
        return AccountType.CREDIT

    @cached_property
    def debit_header(self) -> str | None:
        if self.debit_config and self.debit_config.debit_account_identifier:
            for line in self.pages[0].lines:
                if re.search(self.debit_config.debit_account_identifier, line):
                    return line.lower()
        return None

    @staticmethod
    def get_identifiers(parser: PdfParser) -> list[Any]:
        identifiers = []
        # pylint: disable=protected-access
        if parser.extractor.encrypt_dict:
            extractor = parser.extractor
            major, minor = extractor.pdf._header_version
            pdf_version = f"{major}.{minor}"
            encryption_identifier = EncryptionIdentifier(
                float(pdf_version),
                extractor.algorithm,
                extractor.revision,
                extractor.length,
                extractor.permissions,
            )
            identifiers.append(encryption_identifier)

        if metadata := parser.document.metadata:
            metadata_identifier = MetadataIdentifier(**metadata)
            identifiers.append(metadata_identifier)  # type: ignore

        if not identifiers:
            raise ValueError(f"Could not get identifier for {parser.file_path}")

        return identifiers
