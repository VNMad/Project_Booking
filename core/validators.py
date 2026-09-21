import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



def validate_positive_price(value):
    """
    Validate that the rental price is not negative.

    The validator expects a Money value and checks its numeric amount.
    Zero is allowed.
    """
    if value.amount < 0:
        raise ValidationError("Price per night cannot be negative.")


def validate_password(value):
    """
    Validate the password against the project's password requirements.

    The password must contain at least 8 characters, including:
    - one lowercase letter;
    - one uppercase letter;
    - one digit;
    - one special character.
    """
    if not re.fullmatch(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}', value):
        raise ValidationError(
            _('Password is not valid. '
              'It must contain at least 8 characters, '
              'one uppercase letter, one lowercase letter, '
              'one digit and one special character.')
        )


def validate_phone(value):
    """
    Validate an international phone number.

    The phone number must:
    - start with '+';
    - contain only digits after '+';
    - contain from 7 to 15 digits.
    """
    if not re.fullmatch(r'\+[0-9]{7,15}', value):
        raise ValidationError(
            _(
                'Phone number must start with (+) and contain from 7 to 15 digits.'
            )
        )