import pytest
from django.core.exceptions import ValidationError

from core.validators import (
    validate_password,
    validate_phone,
    validate_positive_price,
)
from djmoney.money import Money


@pytest.mark.parametrize(
    "phone",
    [
        "+491234567890",
        "+380501234567",
        "+442071234567",
        "+33123456789",
        "+1234567",
        "+123456789012345",
    ],
)
def test_validate_phone_accepts_valid_phone(phone):
    """
    Check that valid international phone numbers pass validation.
    """
    validate_phone(phone)


@pytest.mark.parametrize(
    "phone",
    [
        "491234567890",
        "380501234567",
        "+49 1234567890",
        "+49-1234567890",
        "+49123456789A",
        "+123456",
        "+1234567890123456",
    ],
)
def test_validate_phone_rejects_invalid_phone(phone):
    """
    Check that invalid phone numbers raise ValidationError.
    """
    with pytest.raises(ValidationError):
        validate_phone(phone)


def test_validate_password_accepts_valid_password():
    """
    Check that a valid password passes validation.
    """
    validate_password("TestPassword1!")


@pytest.mark.parametrize(
    "password",
    [
        "short1!",
        "PASSWORD1!",
        "password1!",
        "Password!",
        "Password1",
    ],
)
def test_validate_password_rejects_invalid_password(password):
    """
    Check that invalid passwords raise ValidationError.
    """
    with pytest.raises(ValidationError):
        validate_password(password)


@pytest.mark.parametrize(
    "price",
    [
        Money("0.00", "EUR"),
        Money("100.00", "EUR"),
        Money("999.99", "EUR"),
    ],
)
def test_validate_positive_price_accepts_valid_price(price):
    """
    Check that zero and positive prices pass validation.
    """
    validate_positive_price(price)


def test_validate_positive_price_rejects_negative_price():
    """
    Check that a negative price raises ValidationError.
    """
    with pytest.raises(ValidationError):
        validate_positive_price(Money("-1.00", "EUR"))