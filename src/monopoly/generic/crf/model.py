"""
Thin wrapper around ``sklearn-crfsuite`` for the token-labeling spike.

Training uses L-BFGS, which is deterministic given the data and hyperparameters,
so the same fixtures always yield the same model -- there is no random seed to
set. Importing this module requires the optional ``crf`` extra.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

from . import CRF_EXTRA_HINT
from .features import line_features

try:
    import sklearn_crfsuite
except ImportError as _err:  # pragma: no cover - exercised only without the extra
    raise ImportError(CRF_EXTRA_HINT) from _err

FeatureSeq = list[dict[str, Any]]
LabelSeq = list[str]

# Deterministic, mild-regularization defaults; callers may override per experiment.
DEFAULT_PARAMS: dict[str, Any] = {
    "algorithm": "lbfgs",
    "c1": 0.1,
    "c2": 0.1,
    "max_iterations": 200,
    "all_possible_transitions": True,
}


class TransactionCRF:
    """A CRF that labels statement-line tokens as DATE/DESC/AMOUNT/BALANCE/O."""

    def __init__(self, **params: Any) -> None:
        self._crf = sklearn_crfsuite.CRF(**{**DEFAULT_PARAMS, **params})

    def train(self, feature_seqs: list[FeatureSeq], label_seqs: list[LabelSeq]) -> TransactionCRF:
        """Fit the model on token-feature sequences and their gold labels."""
        self._crf.fit(feature_seqs, label_seqs)
        return self

    def predict(self, feature_seqs: list[FeatureSeq]) -> list[LabelSeq]:
        """Predict a label sequence for each feature sequence."""
        # sklearn-crfsuite returns numpy arrays; hand back plain lists of str.
        return [[str(label) for label in seq] for seq in self._crf.predict(feature_seqs)]

    def predict_line(self, line: str) -> LabelSeq:
        """Featurize and label a single raw statement line."""
        return [str(label) for label in self._crf.predict_single(line_features(line))]

    def save(self, path: Path | str) -> None:
        """Serialize the fitted model to ``path``."""
        Path(path).write_bytes(pickle.dumps(self._crf))

    @classmethod
    def load(cls, path: Path | str) -> TransactionCRF:
        """Load a model previously written by :meth:`save`."""
        model = cls.__new__(cls)
        # Trusted local artifact produced by save(), never untrusted input.
        model._crf = pickle.loads(Path(path).read_bytes())  # noqa: S301, SLF001
        return model
