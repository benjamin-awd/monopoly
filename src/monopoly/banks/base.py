import logging
from typing import Any

from monopoly.config import PdfConfig, StatementConfig

logger = logging.getLogger(__name__)


class BankBase:
    """
    Abstract class to handle initialization of common variables
    that are shared between bank processor classes.

    Ensures consistency between bank classes.
    """

    statement_configs: list[StatementConfig]
    pdf_config: PdfConfig = PdfConfig()
    identifiers: list[list[Any]]

    def __init_subclass__(cls, **kwargs) -> None:
        if not hasattr(cls, "statement_configs"):
            raise NotImplementedError(
                f"{cls.__class__.__name__} "
                "must implement `statement_configs` class variable"
            )
        if not hasattr(cls, "identifiers"):
            raise NotImplementedError(
                f"{cls.__class__.__name__} "
                "must implement `identifiers` class variable"
            )
        return super().__init_subclass__(**kwargs)
