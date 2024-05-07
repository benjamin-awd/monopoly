import logging
from dataclasses import Field, fields
from itertools import product
from pathlib import Path
from typing import Optional, Type, Dict

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
from .bank_of_america import BankOfAmerica

processors: list[Type[ProcessorBase]] = [
    Citibank,
    Dbs,
    ExampleBankProcessor,
    Hsbc,
    Ocbc,
    StandardChartered,
    BankOfAmerica,
]


logger = logging.getLogger(__name__)


class UnsupportedBankError(Exception):
    """Raised when a processor cannot be found for a specific bank"""


def extract_metadata(parser: PdfParser) -> Dict[str, str]:
    """
    Extracts metadata from the PDF using the provided parser.
    """
    metadata = parser.get_metadata()
    return {
        key: str(value)
        for key, value in metadata.items()
    }


def detect_processor(
    file_path: Optional[Path] = None,
    file_bytes: Optional[bytes] = None,
    passwords: Optional[list[SecretStr]] = None,
) -> ProcessorBase:
    """
    Reads the encryption metadata or actual metadata (if the PDF is not encrypted),
    and checks for a bank based on unique identifiers.
    """
    parser = PdfParser(
        file_path=file_path,
        file_bytes=file_bytes,
        pdf_config=PdfConfig(passwords=passwords),
    )

    # Extract and print all metadata
    metadata = extract_metadata(parser)
    logger.info("Extracted PDF Metadata:")
    for key, value in metadata.items():
        logger.info(f"  {key}: {value}")

    # add a debug statement here
    logger.debug("Checking for supported bank: %s", processors)
    for processor in processors:
        metadata_items = processor.get_identifiers(parser)
        logger.debug(
            "Checking bank %s for metadata %s", processor.__name__, metadata_items
        )
        if is_bank_identified(metadata_items, processor):
            logger.debug(f"Matched processor {processor.__name__}")
            return processor(
                file_path=file_path, file_bytes=file_bytes, passwords=passwords
            )
        else:
            logger.debug(f"Processor {processor.__name__} does not match")

    logger.error("No matching processor found")
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
            logger.debug(f"Bank {processor.__name__} identified")
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
            if identifier_value in field_value:
                logger.debug(f"Field {field.name} matches: {identifier_value} in {field_value}")
                return True
            else:
                logger.debug(f"Field {field.name} does not match: {identifier_value} not in {field_value}")
                return False

        # otherwise check that values match exactly
        return identifier_value == field_value
    return False
