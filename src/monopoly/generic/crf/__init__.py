"""
Optional CRF token-classification spike for the generic parser.

This is an offline research spike (see
``.claude/plans/2026-09-05-crf-generic-parser-spike.md``): it measures whether a
CRF token classifier recovers transaction lines better than the current layout
heuristic. It is deliberately *not* wired into the live extraction path.

The package is import-safe without the optional ``crf`` extra so the core
library never hard-depends on ``sklearn-crfsuite``. Call :func:`require_crf`
before using anything that needs the model.
"""

CRF_EXTRA_HINT = "The CRF spike requires the 'crf' extra: pip install 'monopoly-core[crf]'"


def require_crf() -> None:
    """Raise a clear ``ImportError`` if the optional CRF dependency is missing."""
    try:
        import sklearn_crfsuite  # noqa: F401
    except ImportError as err:
        raise ImportError(CRF_EXTRA_HINT) from err


__all__ = ["CRF_EXTRA_HINT", "require_crf"]
