from pytest import raises
from test_utils.skip import skip_if_encrypted

from monopoly.banks import auto_detect_bank
from monopoly.banks.base import BankBase
from monopoly.constants import EncryptionIdentifier, MetadataIdentifier


class MockBankOne(BankBase):
    statement_config = None
    transaction_config = None
    identifiers = [
        EncryptionIdentifier(
            pdf_version=1.7, algorithm=5, revision=6, length=256, permissions=-1028
        ),
        MetadataIdentifier(creator="foo", producer="bar"),
    ]


class MockBankTwo(BankBase):
    statement_config = None
    transaction_config = None
    identifiers = [
        MetadataIdentifier(
            creator="Adobe Acrobat 23.3", producer="Adobe Acrobat Pro (64-bit)"
        )
    ]


unencrypted_file_path = "tests/integration/banks/example/input.pdf"
encrypted_file_path = "tests/integration/fixtures/protected.pdf"


@skip_if_encrypted
def test_auto_detect_unencrypted_bank_identified(
    monkeypatch, file_path: str = unencrypted_file_path
):
    mock_banks_list = [MockBankOne, MockBankTwo]
    monkeypatch.setattr("monopoly.banks.banks", mock_banks_list)
    bank_instance = auto_detect_bank(
        file_path=file_path,
    )
    assert isinstance(bank_instance, MockBankTwo)


def test_auto_detect_encrypted_bank_identified(
    monkeypatch, file_path: str = encrypted_file_path
):
    mock_banks_list = [MockBankOne, MockBankTwo]
    monkeypatch.setattr("monopoly.banks.banks", mock_banks_list)
    bank_instance = auto_detect_bank(
        file_path=file_path,
    )
    assert isinstance(bank_instance, MockBankOne)


@skip_if_encrypted
def test_auto_detect_bank_not_identified(
    monkeypatch, file_path: str = unencrypted_file_path
):
    mock_banks_list = [MockBankOne]
    monkeypatch.setattr("monopoly.banks.banks", mock_banks_list)

    with raises(ValueError, match=f"Could not find a bank for {file_path}"):
        auto_detect_bank(file_path=file_path)
