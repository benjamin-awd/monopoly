import logging
from abc import ABC, abstractmethod
from typing import Optional

from pydantic import SecretStr

from monopoly.config import CreditStatementConfig, DebitStatementConfig, PdfConfig
from monopoly.constants import EncryptionIdentifier, MetadataIdentifier

logger = logging.getLogger(__name__)


class BankBase(ABC):
    """
    Abstract class to handle initialization of common variables
    that are shared between bank processor classes.

    Ensures consistency between bank classes.
    """

    credit_config: Optional[CreditStatementConfig] = None
    debit_config: Optional[DebitStatementConfig] = None
    # pdf_config defaults to an empty object if not overriden
    pdf_config: PdfConfig = PdfConfig()

    def __init__(self, generic=False):
        self.validate_config(generic)
        self.populate_pdf_config()

    def validate_config(self, generic: bool):
        # Basic validation to ensure required attributes are set
        if not generic:
            if self.credit_config is None and self.debit_config is None:
                raise NotImplementedError(
                    f"{self.__class__.__name__} "
                    "must implement either `credit_config` or `debit_config`"
                )

    def populate_pdf_config(self):
        # Ensure that PDF config always exists
        if not self.pdf_config:
            self.pdf_config = PdfConfig()
            logger.info(f"{self.__class__.__name__}: Using default `pdf_config`")

    @property
    @abstractmethod
    def identifiers(self) -> list[EncryptionIdentifier | MetadataIdentifier]:
        raise NotImplementedError("Identifiers must be defined")

    @property
    def passwords(self) -> Optional[list[SecretStr]]:
        if self.passwords:
            return self.passwords
        return None
