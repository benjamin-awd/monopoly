import logging
from typing import ClassVar

from monopoly.config import PdfConfig, StatementConfig
from monopoly.identifiers import Identifier, IdentifierGroup

logger = logging.getLogger(__name__)


class BankBase:
    """
    Handle initialization of common variables that are shared between bank processor classes.

    Ensures consistency between bank classes.
    """

    registry: ClassVar[list[type["BankBase"]]] = []

    name: ClassVar[str]
    statement_configs: ClassVar[list[StatementConfig]]
    pdf_config: PdfConfig = PdfConfig()
    identifiers: ClassVar[list["IdentifierGroup"]]

    def __init_subclass__(cls, **kwargs) -> None:
        required_attrs = ("statement_configs", "identifiers", "name")
        for attr in required_attrs:
            if not hasattr(cls, attr):
                msg = f"{cls.__name__} must implement `{attr}` class variable"
                raise NotImplementedError(msg)

        # structural validation only applies to regular banks (not GenericBank)
        if cls.identifiers:
            cls._validate_identifiers()
            cls._validate_name()
            cls._validate_statement_configs()
            cls.registry.append(cls)

        return super().__init_subclass__(**kwargs)

    @classmethod
    def _validate_identifiers(cls) -> None:
        if not all(isinstance(group, list) for group in cls.identifiers):
            msg = (
                f"{cls.__name__}: `identifiers` must be a list of lists, e.g. "
                "[[MetadataIdentifier(...), TextIdentifier(...)]]"
            )
            raise TypeError(msg)

        for item in (item for group in cls.identifiers for item in group):
            if not isinstance(item, Identifier):
                msg = (
                    f"{cls.__name__}: each identifier must be an instance of "
                    f"Identifier, got {type(item).__name__}: {item!r}"
                )
                raise TypeError(msg)

    @classmethod
    def _validate_name(cls) -> None:
        if not isinstance(cls.name, str) or not cls.name.strip():
            msg = f"{cls.__name__}: `name` must be a non-empty string"
            raise ValueError(msg)

        existing_names = {bank.name for bank in cls.registry}
        if cls.name in existing_names:
            conflict = next(b for b in cls.registry if b.name == cls.name)
            msg = f"{cls.__name__}: duplicate bank name {cls.name!r}, already used by {conflict.__name__}"
            raise ValueError(msg)

    @classmethod
    def _validate_statement_configs(cls) -> None:
        if not isinstance(cls.statement_configs, list) or not cls.statement_configs:
            msg = f"{cls.__name__}: `statement_configs` must be a non-empty list of StatementConfig instances"
            raise TypeError(msg)

        required_groups = {"description", "amount"}
        for config in cls.statement_configs:
            if not isinstance(config, StatementConfig):
                msg = (
                    f"{cls.__name__}: each statement_config must be an instance of "
                    f"StatementConfig, got {type(config).__name__}: {config!r}"
                )
                raise TypeError(msg)

            pattern = config.transaction_pattern
            actual_pattern = getattr(pattern, "regex", pattern)
            group_index = getattr(actual_pattern, "groupindex", None)
            if group_index is None:
                continue
            missing = required_groups - group_index.keys()
            if missing:
                msg = (
                    f"{cls.__name__}: transaction pattern {pattern!r} is missing "
                    f"required named groups: {', '.join(sorted(missing))}"
                )
                raise ValueError(msg)
