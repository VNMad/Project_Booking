import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_password(value):
    if not re.fullmatch(
            r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}',
            value
    ):
        raise ValidationError(
            _('Password is not valid. '
              'It must contain at least 8 characters, '
              'one uppercase letter, one lowercase letter, '
              'one digit and one special character.')
        )