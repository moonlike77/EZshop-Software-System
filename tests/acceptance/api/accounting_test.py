import pytest
from app.models.DTO.transaction_dto import TransactionCreateDTO
from pydantic import ValidationError
from app.models.transaction_type import TransactionType

# ---------------------------------------------------------------------
# VALIDATION TESTS
# ---------------------------------------------------------------------

def test_validation_transaction_negative_amount():
    try:
        TransactionCreateDTO(
            amount=-50.0,
            type=TransactionType.CREDIT,
            description="Invalid transaction"
        )
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "Amount must be positive" in str(e) or "Value error, Amount must be positive" in str(e)

def test_validation_transaction_zero_amount():
    try:
        TransactionCreateDTO(
            amount=0.0,
            type=TransactionType.CREDIT,
            description="Invalid transaction"
        )
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "Amount must be positive" in str(e)
