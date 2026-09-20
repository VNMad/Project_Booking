from apps.users.serializers import RegisterSerializer, UserSerializer


def test_register_serializer_accepts_valid_password(db):
    """
    Check that RegisterSerializer accepts a valid password.
    """
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "newuser@example.com",
        "phone": "+491234567890",
        "password": "TestPassword1!",
    }

    serializer = RegisterSerializer(data=data)

    assert serializer.is_valid() is True
    assert "password" not in serializer.errors


def test_register_serializer_rejects_invalid_password(db):
    """
    Check that RegisterSerializer rejects an invalid password.
    """
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "newuser@example.com",
        "phone": "+491234567890",
        "password": "password123",
    }

    serializer = RegisterSerializer(data=data)

    assert serializer.is_valid() is False
    assert "password" in serializer.errors


def test_register_serializer_rejects_invalid_email(db):
    """
    Check that RegisterSerializer rejects an invalid email.
    """
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "invalid-email",
        "phone": "+491234567890",
        "password": "TestPassword1!",
    }

    serializer = RegisterSerializer(data=data)

    assert serializer.is_valid() is False
    assert "email" in serializer.errors


def test_register_serializer_rejects_existing_email(user):
    """
    Check that RegisterSerializer rejects an email
    that already exists in the database.
    """
    data = {
        "first_name": "Another",
        "last_name": "User",
        "email": user.email,
        "phone": "+491111111111",
        "password": "TestPassword1!",
    }

    serializer = RegisterSerializer(data=data)

    assert serializer.is_valid() is False
    assert "email" in serializer.errors


def test_register_serializer_rejects_missing_phone(db):
    """
    Check that RegisterSerializer rejects registration
    data without the required phone field.
    """
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "newuser@example.com",
        "password": "TestPassword1!",
    }

    serializer = RegisterSerializer(data=data)

    assert serializer.is_valid() is False
    assert "phone" in serializer.errors


def test_user_serializer_returns_user_data(user):
    """
    Check that UserSerializer returns the expected user data.
    """
    serializer = UserSerializer(user)

    assert serializer.data["first_name"] == "Test"
    assert serializer.data["last_name"] == "Tenant"
    assert serializer.data["email"] == "tenant@example.com"
    assert serializer.data["phone"] == "+491234567890"
    assert serializer.data["is_active"] is True


def test_user_serializer_does_not_return_password(user):
    """
    Check that UserSerializer does not expose the user's password.
    """
    serializer = UserSerializer(user)

    assert "password" not in serializer.data


def test_user_serializer_read_only_fields(user):
    """
    Check that protected user fields are read-only.
    """
    serializer = UserSerializer(user)

    assert serializer.fields["email"].read_only is True
    assert serializer.fields["is_active"].read_only is True
    assert serializer.fields["created_at"].read_only is True
    assert serializer.fields["updated_at"].read_only is True

