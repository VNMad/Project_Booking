def test_user_creation(user):
    """
    Check that a test user is created correctly.
    """
    assert user.email == "tenant@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "Tenant"
    assert user.phone == "+491234567890"
    assert user.is_active is True