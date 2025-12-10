import re
from monopoly.config import MultilineConfig, StatementConfig, EntryType
from monopoly.statements.base import BaseStatement
from monopoly.statements.transaction import TransactionMatch


def test_carry_forward_date_when_multiline_is_enabled():
    """
    Tests that pre_process_match correctly carries forward a transaction date
    to subsequent transactions when the feature is enabled in the config.

    This simulates a statement where a date appears once, and all following transactions
    on that page are assumed to share that date until a new one appears.
    """
    multiline_config = MultilineConfig(multiline_transaction_date=True)
    config = StatementConfig(
        multiline_config=multiline_config,
        transaction_pattern=".*",
        statement_date_pattern=".*",
        statement_type=EntryType.CREDIT,
        header_pattern=".*",
        transaction_auto_polarity=True,
    )
    statement = BaseStatement(pages=[], bank_name="Test Bank", config=config, header="")

    # SCENARIO: Process a sequence of transactions
    first_date = "24 FEB 2025"
    dummy_match = re.search("foo", "foo")

    # Transaction 1: Has a date. This date should be saved as 'previous_transaction_date'.
    tx_with_date_1 = TransactionMatch(
        description="ONLINE PAYMENT TO VENDOR X",
        amount="150.00",
        transaction_date=first_date,
        polarity=None,
        match=dummy_match,
        page_number=0,
    )
    result_1 = statement.pre_process_match(tx_with_date_1)
    assert result_1.transaction_date == first_date
    assert statement.previous_transaction_date == first_date, "The first date should be stored immediately"

    # Transaction 2: Has no date. It should inherit the date from the first transaction.
    tx_without_date_1 = TransactionMatch(
        description="ANOTHER TRANSACTION X",
        amount="200.00",
        transaction_date=None,
        polarity=None,
        match=dummy_match,
        page_number=0,
    )
    result_2 = statement.pre_process_match(tx_without_date_1)
    assert result_2.transaction_date == first_date, "The second transaction should inherit the first date"

    # Transaction 3: Has a new date. This should update the 'previous_transaction_date'.
    second_date = "25 FEB 2025"
    tx_with_date_2 = TransactionMatch(
        description="SOME OTHER TRANSACTION",
        amount="150.00",
        transaction_date=second_date,
        polarity=None,
        match=dummy_match,
        page_number=0,
    )
    result_3 = statement.pre_process_match(tx_with_date_2)
    assert result_3.transaction_date == second_date, "The third transaction should have its new date"
    assert statement.previous_transaction_date == second_date, "The previous date should be updated"

    # Transaction 4: Has no date. It should inherit the new date from the third transaction.
    tx_without_date_2 = TransactionMatch(
        description="FINAL TRANSACTION",
        amount="120.00",
        transaction_date=None,
        polarity=None,
        match=dummy_match,
        page_number=0,
    )
    result_4 = statement.pre_process_match(tx_without_date_2)
    assert result_4.transaction_date == second_date, "The fourth transaction should inherit the new date"


def test_date_is_not_carried_forward_when_multiline_is_disabled():
    """
    Tests that if multiline_transaction_date is disabled, a missing transaction date
    remains None and is not filled from a previous transaction.
    """
    multiline_config = MultilineConfig(multiline_transaction_date=False)
    config = StatementConfig(
        multiline_config=multiline_config,
        transaction_pattern=".*",
        statement_date_pattern=".*",
        header_pattern=".*",
        statement_type=EntryType.CREDIT,
        transaction_auto_polarity=True,
    )
    statement = BaseStatement(pages=[], bank_name="Test Bank", config=config, header="")
    dummy_match = re.search("foo", "foo")

    # SCENARIO: Process two transactions
    # Process one with a date to set the internal state
    statement.pre_process_match(
        TransactionMatch(
            description="First",
            amount="100.00",
            transaction_date="24 FEB 2025",
            polarity=None,
            match=dummy_match,
            page_number=0,
        )
    )

    # Now process one without a date
    tx_without_date = TransactionMatch(
        description="Second",
        amount="50.00",
        transaction_date=None,
        polarity=None,
        match=dummy_match,
        page_number=0,
    )
    result = statement.pre_process_match(tx_without_date)

    # 3. ASSERT: The date should remain None because the feature is off
    assert result.transaction_date is None, "Date should not be carried forward when the feature is disabled"
