# monopoly/detectors/bank_detector.py

import logging
from typing import TYPE_CHECKING

from monopoly.identifiers import Identifier  # Import base class
from monopoly.pdf import PdfDocument

if TYPE_CHECKING:
    from monopoly.banks.base import BankBase

logger = logging.getLogger(__name__)


class BankDetector:
    def __init__(self, document: PdfDocument):
        self.document = document
        self.metadata_identifier = document.metadata_identifier

    def detect_bank(self, banks: list[type["BankBase"]]) -> type["BankBase"] | None:
        """Detect the bank by checking its identifier groups against the document."""
        logger.debug("Found PDF properties: %s", self.metadata_identifier)
        for bank in banks:
            # A bank is identified if ANY of its identifier groups is a full match
            if any(self.identifiers_match(group) for group in bank.identifiers):
                logger.debug("Identified statement bank: %s", bank.__name__)
                return bank
        return None

    def identifiers_match(self, identifiers: list[Identifier]) -> bool:
        """
        Check if ALL identifiers in a given group match the document.

        An empty group of identifiers does not constitute a match.
        """
        if not identifiers:
            return False

        # Polymorphically call .matches() on each identifier in the group.
        # ALL of them must return True for the group to match.
        return all(identifier.matches(self) for identifier in identifiers)
