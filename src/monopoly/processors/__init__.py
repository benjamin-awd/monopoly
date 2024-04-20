import logging
from dataclasses import Field, fields
from itertools import product
from pathlib import Path
from typing import Optional, Type

from pydantic import SecretStr

from monopoly.config import PdfConfig
from monopoly.constants import EncryptionIdentifier, MetadataIdentifier
from monopoly.pdf import PdfParser

from .base import ProcessorBase
from .citibank import Citibank
from .dbs import Dbs
from .example_bank import ExampleBankProcessor
from .hsbc import Hsbc
from .ocbc import Ocbc
from .standard_chartered import StandardChartered

processors: list[Type[ProcessorBase]] = [
    Citibank,
    Dbs,
    ExampleBankProcessor,
    Hsbc,
    Ocbc,
    StandardChartered,
]


logger = logging.getLogger(__name__)


class UnsupportedBankError(Exception):
    """Raised when a processor cannot be found for a specific bank"""


def detect_processor(
    file_path: Path, passwords: Optional[list[SecretStr]] = None
) -> ProcessorBase:
    """
    Reads the encryption metadata or actual metadata (if the PDF is not encrypted),
    and checks for a bank based on unique identifiers.
    """
    parser = PdfParser(file_path, pdf_config=PdfConfig(passwords=passwords))
    for processor in processors:
        metadata_items = processor.get_identifiers(parser)
        if is_bank_identified(metadata_items, processor):
            return processor(file_path=file_path, passwords=passwords)

    raise UnsupportedBankError("This bank is currently unsupported")


def is_bank_identified(
    metadata_items: list[EncryptionIdentifier | MetadataIdentifier],
    processor: Type[ProcessorBase],
) -> bool:
    """
    Checks if a bank is identified based on a list of metadata items.
    """
    for identifier, metadata in product(processor.identifiers, metadata_items):
        logger.debug(
            "Comparing bank %s identifier %s against PDF metadata %s",
            processor.__name__,
            identifier,
            metadata,
        )
        if all(
            check_matching_field(field, metadata, identifier)
            for field in fields(metadata)
        ):
            return True
    return False


def check_matching_field(
    field: Field,
    metadata: EncryptionIdentifier | MetadataIdentifier,
    identifier: EncryptionIdentifier | MetadataIdentifier,
) -> bool:
    """
    Checks if a field in the metadata matches the corresponding identifier field.
    """
    # Only compare matching identifier types
    if type(metadata) is type(identifier):
        field_value = getattr(metadata, field.name)
        identifier_value = getattr(identifier, field.name)

        # allow for partial string matching
        if isinstance(field.type(), str):
            return identifier_value in field_value

        # otherwise check that values match exactly
        return identifier_value == field_value
    return False
