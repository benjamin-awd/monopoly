"""Unit tests for the CRF wrapper. Trains on a tiny synthetic dataset (no PII)."""

from pathlib import Path

from monopoly.generic.crf.features import line_features
from monopoly.generic.crf.labeling import GoldRow, label_line
from monopoly.generic.crf.model import TransactionCRF

# A handful of debit-style lines: date, description, amount, running balance.
SAMPLES = [
    ("01 OCT   ValueVille SG      123.12     2,000.00", GoldRow("01 OCT", "ValueVille SG", -123.12)),
    ("02 OCT   CoffeePlace SG       9.80     1,990.20", GoldRow("02 OCT", "CoffeePlace SG", -9.80)),
    ("05 OCT   BookBarn SG         45.00     1,945.20", GoldRow("05 OCT", "BookBarn SG", -45.00)),
    ("11 OCT   TransitCard SG      30.00     1,915.20", GoldRow("11 OCT", "TransitCard SG", -30.00)),
]


def _dataset():
    features = [line_features(line) for line, _ in SAMPLES]
    labels = [label_line(line, gold) for line, gold in SAMPLES]
    return features, labels


def test_crf_overfits_tiny_training_set():
    features, labels = _dataset()
    crf = TransactionCRF(c1=0.0, c2=0.0, max_iterations=500).train(features, labels)
    # with no regularization and distinct lines, it should memorize the labels
    assert crf.predict(features) == labels


def test_predict_line_recovers_date_and_amount():
    features, labels = _dataset()
    crf = TransactionCRF(c1=0.0, c2=0.0, max_iterations=500).train(features, labels)

    predicted = crf.predict_line(SAMPLES[0][0])
    # tokens: 01 OCT ValueVille SG 123.12 2,000.00
    assert predicted[0] == "DATE"
    assert predicted[4] == "AMOUNT"
    assert predicted[5] == "BALANCE"


def test_save_load_roundtrip_is_identical(tmp_path: Path):
    features, labels = _dataset()
    crf = TransactionCRF().train(features, labels)

    model_path = tmp_path / "model.pkl"
    crf.save(model_path)
    loaded = TransactionCRF.load(model_path)

    assert loaded.predict(features) == crf.predict(features)
