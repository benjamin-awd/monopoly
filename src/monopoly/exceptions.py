"""
Shared exception hierarchy for statement extraction.

These live at the package root (rather than in ``statements.base``) so that
modules which ``statements.base`` itself depends on — notably ``monopoly.pdf``
and ``statements.date_resolver`` — can reference them without a circular
import. They are re-exported from ``monopoly.statements`` for public use.
"""


class ExtractionError(Exception):
    """
    Base class for retryable statement-extraction failures.

    A failure the extraction cascade may recover from by falling through to the
    next tier (bank config -> generic handler -> LLM).
    """


# Each retryable error multiply-inherits from the builtin it was previously
# raised as, so existing `except ValueError`/`except RuntimeError` call sites
# and tests keep working while the cascade can catch ExtractionError.
class NoTransactionsFoundError(ExtractionError, ValueError):
    """Raised when no transactions could be extracted from a statement."""


class MissingHeaderError(ExtractionError, RuntimeError):
    """Raised when the statement header cannot be located."""


class MissingStatementDateError(ExtractionError, ValueError):
    """Raised when the statement date cannot be resolved."""
