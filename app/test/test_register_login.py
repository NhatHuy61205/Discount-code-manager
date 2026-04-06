import pytest
from unittest.mock import patch
from app.test.test_base import test_session, test_app
from app.models import User
from app import dao


@pytest.fixture
def sample_user(test_session):
    return dao.register_user(
        name="Nguyen Van A",
        username="nva123",
        email="nva@gmail.com",
        phone="0123456789",
        address="123 HCMC",
        password="Password123@!",
        confirm="Password123@!"
    )


# Test thiếu thông tin
def test_register_missing_fields(test_session):
    with pytest.raises(ValueError, match="Vui lòng nhập đầy đủ thông tin"):
        dao.register_user("", "user", "e@mail.com", "0123456789", "Addr", "Pass123!", "Pass123!")

    with pytest.raises(ValueError, match="Vui lòng nhập đầy đủ thông tin"):
        dao.register_user("ABC", "", "e@mail.com", "0123456789", "Addr", "Pass123!", "Pass123!")

    with pytest.raises(ValueError, match="Vui lòng nhập đầy đủ thông tin"):
        dao.register_user("ABC", "user", "", "0123456789", "Addr", "Pass123!", "Pass123!")

    with pytest.raises(ValueError, match="Vui lòng nhập đầy đủ thông tin"):
        dao.register_user("", "user", "e@mail.com", "", "Addr", "Pass123!", "Pass123!")

    with pytest.raises(ValueError, match="Vui lòng nhập đầy đủ thông tin"):
        dao.register_user("", "user", "e@mail.com", "0123456789", "", "Pass123!", "Pass123!")

    with pytest.raises(ValueError, match="Vui lòng nhập đầy đủ thông tin"):
        dao.register_user("", "user", "e@mail.com", "0123456789", "Addr", "", "Pass123!")

    with pytest.raises(ValueError, match="Vui lòng nhập đầy đủ thông tin"):
        dao.register_user("", "user", "e@mail.com", "0123456789", "Addr", "Pass123!", "")

#định dạng số điện thoại
def test_register_invalid_phone(test_session):
    with pytest.raises(ValueError, match="Số điện thoại phải đúng 10 chữ số"):
        dao.register_user("Name", "user", "e@mail.com", "123", "Addr", "Pass123!", "Pass123!")

# đăng ký thành công
def test_register_user_success(test_session):
    user = dao.register_user(
        name="Test User",
        username="testuser",
        email="test@test.com",
        phone="0987654321",
        address="Test Address",
        password="ValidPassword123!",
        confirm="ValidPassword123!"
    )

    assert user is not None
    assert user.username == "testuser"

    db_user = User.query.filter_by(username="testuser").first()
    assert db_user is not None
    assert db_user.email == "test@test.com"


# trùng tên đăng nhập
def test_register_duplicate_username(test_session, sample_user):
    with pytest.raises(ValueError, match="Tên đăng nhập đã tồn tại"):
        dao.register_user(
            name="Nguyen Van B",
            username="nva123",
            email="nvb@gmail.com",
            phone="0999999999",
            address="Hanoi",
            password="Password123@!",
            confirm="Password123@!"
        )

#trùng Email
def test_register_duplicate_email(test_session, sample_user):
    with pytest.raises(ValueError, match="Email đã tồn tại"):
        dao.register_user(
            name="User B",
            username="userb",
            email="nva@gmail.com",
            phone="0888888888",
            address="Hanoi",
            password="Password123@!",
            confirm="Password123@!"
        )

#trùng Email
def test_register_duplicate_phone(test_session, sample_user):
    with pytest.raises(ValueError, match="Số điện thoại đã được sử dụng"):
        dao.register_user(
            name="User B",
            username="userb",
            email="nvb@gmail.com",
            phone="0123456789",
            address="Hanoi",
            password="Password123@!",
            confirm="Password123@!"
        )

# kiểm tra mật khẩu, thiếu trường hợp mật khẩu phải chứ ký tự và ký tự đặc biệt
def test_register_password_validation(test_session):
    with pytest.raises(ValueError, match="Mật khẩu phải tối thiểu 8 ký tự"):
        dao.register_user("A", "usr1", "a@mail.com", "0111111111", "Add", "Pass1!", "Pass1!")

    with pytest.raises(ValueError, match="Mật khẩu phải chứa số"):
        dao.register_user("A", "usr2", "b@mail.com", "0222222222", "Add", "Password!", "Password!")

    with pytest.raises(ValueError, match="Mật khẩu không khớp"):
        dao.register_user("A", "usr3", "c@mail.com", "0333333333", "Add", "Pass123!@", "Pass123!#")

    with pytest.raises(ValueError, match="Mật khẩu phải chứa chữ"):
        dao.register_user("A", "usr3", "c@mail.com", "0333333333", "Add", "123456789", "123456789")

    with pytest.raises(ValueError, match="Mật khẩu phải chứa ký tự đặc biệt"):
        dao.register_user("A", "usr3", "c@mail.com", "0333333333", "Add", "Pass12345", "Pass12345")


# Đăng nhập thành công
def test_auth_user_success(test_session, sample_user):
    # Đảm bảo user active
    sample_user.active = True
    test_session.commit()

    user = dao.auth_user(username="nva123", password="Password123@!")
    assert user is not None
    assert user.username == "nva123"


# sai mật khẩu
def test_auth_user_wrong_password(test_session, sample_user):
    user = dao.auth_user(username="nva123", password="WrongPassword123@!")
    assert user is None


# tài khoản bị khóa hoặc là chưa được kích hoạt
def test_auth_user_inactive(test_session, sample_user):
    sample_user.active = False
    test_session.commit()

    user = dao.auth_user(username="nva123", password="Password123@!")
    assert user is None


# workflow
@patch("app.dao.get_user_by_username", return_value=None)
@patch("app.dao.get_user_by_email", return_value=None)
@patch("app.dao.get_user_by_phone", return_value=None)
@patch("app.db.session.add")
@patch("app.db.session.commit")
def test_register_user_with_mock(mock_commit, mock_add, mock_phone, mock_email, mock_username, test_app):
    with test_app.app_context():
        user = dao.register_user(
            name="Mock User",
            username="mockuser",
            email="mock@test.com",
            phone="0555555555",
            address="Mock Addr",
            password="Password123@!",
            confirm="Password123@!"
        )

        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        assert user.username == "mockuser"
