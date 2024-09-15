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

    name: str
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
        if not hasattr(cls, "name"):
            raise NotImplementedError(
                f"{cls.__class__.__name__} " "must implement `name` class variable"
            )

        # validation logic only applies to regular banks
        if cls.identifiers:
            if not any(isinstance(item, list) for item in cls.identifiers):
                raise TypeError("`identifiers` must be a list of lists")

        return super().__init_subclass__(**kwargs)
