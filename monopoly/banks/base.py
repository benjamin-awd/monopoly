from typing import Optional

from monopoly.constants import EncryptionIdentifier, MetadataIdentifier
from monopoly.pdf import BruteForceConfig, PdfConfig, PdfParser
from monopoly.processor import StatementProcessor


class BankBase(StatementProcessor):
    """Helper class to handle initialization of common variables
    that are shared between bank classes"""

    def __init__(
        self,
        file_path: str,
        identifiers: Optional[list[EncryptionIdentifier | MetadataIdentifier]] = None,
        password: Optional[str] = None,
        parser: Optional[PdfParser] = None,
    ):
        self.identifiers = identifiers
        self.parser = parser

        # optional config
        self.pdf_config = getattr(self, "pdf_config", PdfConfig())
        self.brute_force_config = getattr(
            self, "brute_force_config", BruteForceConfig()
        )
        self.safety_check_enabled = getattr(self, "safety_check_enabled", True)

        # this allows the user to override the default pydantic password
        # and supply their own password via the bank subclasses
        if password:
            self.pdf_config.password = password

        super().__init__(
            statement_config=self.statement_config,
            safety_check_enabled=self.safety_check_enabled,
            brute_force_config=self.brute_force_config,
            pdf_config=self.pdf_config,
            file_path=file_path,
        )

    @staticmethod
    def get_identifier(parser: PdfParser) -> EncryptionIdentifier | MetadataIdentifier:
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
            return encryption_identifier

        if metadata := parser.document.metadata:
            metadata_identifier = MetadataIdentifier(
                metadata.get("title"),
                metadata.get("author"),
                metadata.get("subject"),
                metadata.get("creator"),
                metadata.get("producer"),
            )
            return metadata_identifier

        raise ValueError(f"Could not get identifier for {parser.file_path}")
