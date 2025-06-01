import logging
from typing import Any, ClassVar

from monopoly.config import PdfConfig, StatementConfig

logger = logging.getLogger(__name__)


class BankBase:
    """
    Handle initialization of common variables that are shared between bank processor classes.

    Ensures consistency between bank classes.
    """

    name: ClassVar[str]
    statement_configs: ClassVar[list[StatementConfig]]
    pdf_config: PdfConfig = PdfConfig()
    identifiers: ClassVar[list[list[Any]]]

    def __init_subclass__(cls, **kwargs) -> None:
        if not hasattr(cls, "statement_configs"):
            msg = f"{cls.__class__.__name__} must implement `statement_configs` class variable"
            raise NotImplementedError(msg)
        if not hasattr(cls, "identifiers"):
            msg = f"{cls.__class__.__name__} must implement `identifiers` class variable"
            raise NotImplementedError(msg)
        if not hasattr(cls, "name"):
            msg = f"{cls.__class__.__name__} must implement `name` class variable"
            raise NotImplementedError(msg)

        # validation logic only applies to regular banks
        if cls.identifiers and not any(isinstance(item, list) for item in cls.identifiers):
            msg = "`identifiers` must be a list of lists"
            raise TypeError(msg)

        return super().__init_subclass__(**kwargs)
