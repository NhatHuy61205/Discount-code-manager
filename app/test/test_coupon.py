import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import MultiDict
from app.test.test_base import test_session, test_app
from app import dao
from app.models import Coupon, DiscountKind, CouponStatus


def get_now(): return (datetime.now() + timedelta(minutes=1)).strftime("%d/%m/%Y %H:%M")
def get_future(day=1): return (datetime.now() + timedelta(days=day)).strftime("%d/%m/%Y %H:%M")
def get_past(day=1): return (datetime.now() - timedelta(days=day)).strftime("%d/%m/%Y %H:%M")


@pytest.fixture
def sample_coupon(test_session):
    coupon = Coupon(
        name="Giảm giá Tết 2026",
        code="TET2026",
        description="Mã giảm giá dịp tết",
        discount_kind=DiscountKind.FIXED,
        discount_value=50000,
        quantity=100,
        status=CouponStatus.ACTIVE,
        start_date=datetime.now() + timedelta(minutes=1),
        end_date=datetime.now() + timedelta(days=30),
        active=True
    )
    test_session.add(coupon)
    test_session.commit()
    return coupon

# chỉ admin tạo mã giảm giá
def test_admin_only_can_create_coupon():
    mock_current_user = MagicMock()
    mock_current_user.is_admin = False

    def route_create_coupon_simulation(user):
        if not user.is_admin:
            raise PermissionError("Chỉ admin mới có quyền tạo mã giảm giá.")
        return True

    with pytest.raises(PermissionError, match="Chỉ admin mới có quyền tạo mã giảm giá."):
        route_create_coupon_simulation(mock_current_user)

    mock_admin = MagicMock()
    mock_admin.is_admin = True

    result = route_create_coupon_simulation(mock_admin)
    assert result is True

def test_create_coupon_missing_name(test_session):
    from_missing_name = MultiDict([
        #("name", ""),
        ("code", "SALE"),
        ("quantity", "100"),
        ("discount_value", "10000"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    with pytest.raises(ValueError, match="Vui lòng nhập tên mã giảm giá."):
        dao.create_coupon_from_form(from_missing_name)

def test_create_coupon_missing_code(test_session):
    from_missing_code = MultiDict([
        ("name", "Giảm giá"),
        #("code", ""),
        ("quantity", "100"),
        ("discount_value", "10000"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    with pytest.raises(ValueError, match="Vui lòng nhập code mã giảm giá."):
        dao.create_coupon_from_form(from_missing_code)

def test_create_coupon_missing_start_date(test_session):
    from_missing_start_date = MultiDict([
        ("name", "Giảm giá"),
        ("code", "SALE"),
        ("quantity", "100"),
        ("discount_value", "10000"),
        #("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    with pytest.raises(ValueError, match="Vui lòng nhập ngày bắt đầu."):
        dao.create_coupon_from_form(from_missing_start_date)

def test_create_coupon_missing_end_date(test_session):
    from_missing_end_date = MultiDict([
        ("name", "Giảm giá"),
        ("code", "SALE"),
        ("quantity", "100"),
        ("discount_value", "10000"),
        ("start_date", get_now()),
        #("end_date", get_future(30))
    ])
    with pytest.raises(ValueError, match="Vui lòng nhập ngày kết thúc."):
        dao.create_coupon_from_form(from_missing_end_date)

# mã giảm giá trùng
def test_coupon_code_must_be_unique(test_session, sample_coupon):
    form_dup_code = MultiDict([
        ("name", "Giảm giá Mùa Hè"),
        ("code", "TET2026"),
        ("quantity", "100"),
        ("discount_value", "10000"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])

    with pytest.raises(ValueError, match="Code mã giảm giá đã tồn tại."):
        dao.create_coupon_from_form(form_dup_code)

    form_dup_code1 = MultiDict([
        ("name", "Giảm giá Mùa Hè"),
        ("code", "SUM2026"),
        ("quantity", "100"),
        ("discount_value", "10000"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    result = dao.create_coupon_from_form(form_dup_code1)
    assert result is not None
    assert result.code == "SUM2026"

# Ngày bắt đầu phải lớn hơn hoặc bằng ngày hiện tại
def test_start_date_must_be_future_or_present(test_session):
    form_past_date = MultiDict([
        ("name", "MÃ GIẢM GIÁ"),
        ("code", "SALE123"),
        ("quantity", "100"),
        ("discount_value", "100000"),
        ("start_date", get_past(1)),
        ("end_date", get_future(30))
    ])
    with pytest.raises(ValueError, match="Thời gian bắt đầu phải lớn hơn hoặc bằng thời điểm hiện tại."):
        dao.create_coupon_from_form(form_past_date)

    form_now = MultiDict([
        ("name", "Mã GIẢM GIÁ"),
        ("code", "SALE123"),
        ("quantity", "100"),
        ("discount_value", "10000"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    result = dao.create_coupon_from_form(form_now)
    assert result is not None
    assert result.code == "SALE123"

    form_future_date = MultiDict([
        ("name", "Mã GIẢM GIÁ"),
        ("code", "SALE1234"),
        ("quantity", "100"),
        ("discount_value", "10000"),
        ("start_date", get_future(2)),
        ("end_date", get_future(30))
    ])
    assert dao.create_coupon_from_form(form_future_date) is not None

# Ngày kết thúc phải lớn hơn hoặc bằng ngày hiện tại
def test_end_date_must_be_future_or_present(test_session):
    form_past_date = MultiDict([
        ("name", "MÃ GIẢM GIÁ"),
        ("code", "SALE123"),
        ("quantity", "100"),
        ("discount_value", "100000"),
        ("start_date", get_now()),
        ("end_date", get_past(30))
    ])
    with pytest.raises(ValueError, match="Thời gian kết thúc không hợp lệ."):
        dao.create_coupon_from_form(form_past_date)

    form_now = MultiDict([
        ("name", "Mã GIẢM GIÁ"),
        ("code", "SALE123"),
        ("quantity", "100"),
        ("discount_value", "10000"),
        ("start_date", get_now()),
        ("end_date", get_now())
    ])
    result = dao.create_coupon_from_form(form_now)
    assert result is not None
    assert result.code == "SALE123"

    form_future_date = MultiDict([
        ("name", "Mã GIẢM GIÁ"),
        ("code", "SALE1234"),
        ("quantity", "100"),
        ("discount_value", "10000"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    assert dao.create_coupon_from_form(form_future_date) is not None

#
def test_discount_value_logic_and_max_50_percent(test_session):
    form_invalid_percent = MultiDict([
        ("name", "Sale 60%"),
        ("code", "SALE60"),
        ("quantity", "100"),
        ("discount_kind", "percentage"),
        ("discount_value", "60"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    with pytest.raises(ValueError, match="Mã giảm theo % không được vượt quá 50%."):
        dao.create_coupon_from_form(form_invalid_percent)

    form_valid_percent = MultiDict([
        ("name", "Sale 50%"),
        ("code", "SALE50"),
        ("quantity", "100"),
        ("discount_kind", "percentage"),
        ("discount_value", "50"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    coupon_percent = dao.create_coupon_from_form(form_valid_percent)
    assert coupon_percent.discount_kind == DiscountKind.PERCENTAGE
    assert coupon_percent.discount_value == 50

    form_valid_fixed = MultiDict([
        ("name", "Giảm 100k"),
        ("code", "SALE100K"),
        ("quantity", "100"),
        ("discount_kind", "fixed"),
        ("discount_value", "100000"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    coupon_fixed = dao.create_coupon_from_form(form_valid_fixed)
    assert coupon_fixed.discount_kind == DiscountKind.FIXED
    assert coupon_fixed.discount_value == 100000

    form_valid_1 = MultiDict([
        ("name", "Giảm 100k"),
        ("code", "SALE001"),
        ("quantity", "100"),
        ("discount_kind", "fixed"),
        ("discount_value", "-100000"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    with pytest.raises(ValueError, match="Mức giảm phải lớn hơn 0."):
        dao.create_coupon_from_form(form_valid_1)

    form_valid_2 = MultiDict([
        ("name", "Giảm 100k"),
        ("code", "SALE002"),
        ("quantity", "100"),
        ("discount_kind", "fixed"),
        ("discount_value", "0"),
        ("start_date", get_now()),
        ("end_date", get_future(30))
    ])
    with pytest.raises(ValueError, match="Mức giảm phải lớn hơn 0."):
        dao.create_coupon_from_form(form_valid_2)

def test_start_data_must_be_less_than_end_date(test_session):
    form1 = MultiDict([
        ("name", "Giảm giá"),
        ("code", "SALE123"),
        ("quantity", "100"),
        ("discount_kind", "fixed"),
        ("discount_value", "100"),
        ("start_date", get_future(10)),
        ("end_date", get_now())
    ])
    with pytest.raises(ValueError, match="Thời gian bắt đầu phải nhỏ hơn hoặc bằng thời gian kết thúc."):
        dao.create_coupon_from_form(form1)

    form2 = MultiDict([
        ("name", "Giảm giá"),
        ("code", "SALE123"),
        ("quantity", "100"),
        ("discount_kind", "fixed"),
        ("discount_value", "100"),
        ("start_date", get_now()),
        ("end_date", get_now())
    ])
    result = dao.create_coupon_from_form(form2)
    assert result.code == "SALE123"

    form3 = MultiDict([
        ("name", "Giảm giá mùa đông 2026"),
        ("code", "SALE999"),
        ("quantity", "100"),
        ("discount_kind", "fixed"),
        ("discount_value", "100"),
        ("start_date", get_future(30)),
        ("end_date", get_future(50))
    ])
    result = dao.create_coupon_from_form(form3)
    assert result.name == "Giảm giá mùa đông 2026"

# ==============================================

def test_update_coupon_success(test_session, sample_coupon):
    form1 = {
        "name": "Giảm giá Tết Cập Nhật",
        "code": "TET2026",
        "description": "Đã update",
        "discount_kind": "fixed",
        "discount_value": 80000,
        "min_order_value": 150000,
        "quantity": 200,
        "max_discount_value": "",
        "start_date": sample_coupon.start_date.strftime("%d/%m/%Y %H:%M"),
        "end_date": "31/12/2026 23:59",
        "status": "ACTIVE"
    }
    updated_coupon = dao.update_coupon_from_form(sample_coupon, form1)

    assert updated_coupon.name == "Giảm giá Tết Cập Nhật"
    assert updated_coupon.code == "TET2026"

def test_update_coupon_duplicate_code(test_session, sample_coupon):
    other_coupon = Coupon(
        name="Mã khác",
        code="OTHER",
        discount_kind=DiscountKind.FIXED,
        discount_value=10,
        status=CouponStatus.ACTIVE
    )
    test_session.add(other_coupon)
    test_session.commit()

    form_data = {
        "name": "Sửa tên",
        "code": "OTHER",
        "description": "",
        "discount_kind": "fixed",
        "discount_value": 10,
        "min_order_value": 10,
        "quantity": 10,
        "max_discount_value": "",
        "start_date": get_now(),
        "end_date": get_future(30),
        "status": "ACTIVE"
    }

    with pytest.raises(ValueError, match="Code mã giảm giá đã tồn tại."):
        dao.update_coupon_from_form(sample_coupon, form_data)

#========================================================

def test_delete_coupon_success(test_session, sample_coupon):
    coupon_id = sample_coupon.id
    dao.delete_coupon_by_id(coupon_id)
    deleted_coupon = test_session.get(Coupon, coupon_id)
    assert deleted_coupon is None

#========================================================
@patch("app.dao.db.session")
@patch("app.dao.CouponProduct.query")
@patch("app.dao.CouponCategory.query")
@patch("app.dao.Cart.query")
@patch("app.models.Order.query")
@patch("app.dao.UserCoupon.query")
@patch("app.dao.Coupon.query")
def test_delete_coupon_mock_workflow(
        mock_coupon_query,
        mock_usercoupon_query,
        mock_order_query,
        mock_cart_query,
        mock_category_query,
        mock_product_query,
        mock_session,
        sample_coupon
):
    mock_coupon_query.get_or_404.return_value = sample_coupon

    mock_usercoupon_query.filter_by.return_value.first.return_value = None
    mock_order_query.filter_by.return_value.first.return_value = None
    mock_cart_query.filter_by.return_value.first.return_value = None

    result = dao.delete_coupon_by_id(99)

    mock_coupon_query.get_or_404.assert_called_once_with(99)

    mock_category_query.filter_by.assert_called_once_with(coupon_id=sample_coupon.id)
    mock_product_query.filter_by.assert_called_once_with(coupon_id=sample_coupon.id)
    mock_category_query.filter_by.return_value.delete.assert_called_once()
    mock_product_query.filter_by.return_value.delete.assert_called_once()

    mock_session.delete.assert_called_once_with(sample_coupon)
    mock_session.commit.assert_called_once()

    assert result == sample_coupon