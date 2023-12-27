from pathlib import Path
from typing import Any, Optional

from monopoly.constants import EncryptionIdentifier, MetadataIdentifier
from monopoly.pdf import PdfConfig, PdfParser
from monopoly.processor import StatementProcessor


class ProcessorBase(StatementProcessor):
    """Helper class to handle initialization of common variables
    that are shared between bank processor classes"""

    identifiers: list[EncryptionIdentifier | MetadataIdentifier]

    def __init__(
        self,
        file_path: Path,
        passwords: Optional[list[str]] = None,
        parser: Optional[PdfParser] = None,
    ):
        self.parser = parser

        # optional config
        self.pdf_config = getattr(self, "pdf_config", PdfConfig())

        # this allows the user to override the default pydantic password
        # and supply their own password via the bank subclasses
        if passwords:
            self.pdf_config.passwords = passwords

        if isinstance(file_path, str):
            file_path = Path(file_path)

        super().__init__(
            credit_config=self.credit_config,
            debit_config=self.debit_config,
            pdf_config=self.pdf_config,
            file_path=file_path,
        )

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
