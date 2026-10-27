from models import User


def test_user_password_hashing_behaves_correctly():
    user = User(username="alice")
    user.set_password("secret123")

    assert user.password_hash != "secret123"
    assert user.check_password("secret123")
    assert not user.check_password("wrong-password")
