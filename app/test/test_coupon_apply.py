import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from sqlalchemy.ext.asyncio import result
from werkzeug.datastructures import MultiDict
from app.test.test_base import test_session, test_app
from app import dao
from app.models import Coupon, DiscountKind, CouponStatus, CouponCondition, CouponProduct, CouponTargetType, User, \
    Category, Product, UserCoupon, Cart, CartItem, CouponCategory, CouponApplyType


def get_past(day=1): return datetime.now() - timedelta(days=day)
def get_now(): return datetime.now() + timedelta(minutes=1)
def get_future(day=1): return datetime.now() + timedelta(days=day)

@pytest.fixture
def sample_user(test_session):
    user = User(
        name="Buyer",
        username="buyer",
        email="buyer@ou.edu.vn",
        password = "Buy123!",
        address = "HCM city",
        phone = "1234567890",
        active=True
    )
    test_session.add(user)
    test_session.commit()
    return user

@pytest.fixture
def sample_category(test_session):
    category = Category(name="Ao", active=True)
    test_session.add(category)
    test_session.commit()
    return category

@pytest.fixture
def sample_product(test_session, sample_category):
    product = Product(
        name="Ao thun",
        price=200000,
        stock_quantity=10,
        cate_id = sample_category.id,
        active=True
    )
    test_session.add(product)
    test_session.commit()
    return product

def test_save_coupon_success(test_session, sample_user):
    coupon = Coupon(
        name = "Giam gia mua mua",
        code = "SALE123",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=10,
        show_public = True,
        status = CouponStatus.ACTIVE,
        quantity = 10,
        active = True,
        start_date = get_past(),
        end_date = get_future(),
    )
    test_session.add(coupon)
    test_session.commit()

    user_coupon = dao.save_coupon_for_user(sample_user, coupon.id)
    assert user_coupon.user_id == sample_user.id
    assert user_coupon.coupon_id == coupon.id
    assert user_coupon.is_used is False

def test_save_coupon_failed_expered(test_session, sample_user):
    coupon = Coupon(
        name = "Giam gia mua mua",
        code = "SALE123",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=10,
        show_public = True,
        status=CouponStatus.ACTIVE,
        quantity=10,
        active=True,
        start_date=get_past(30),
        end_date=get_past(15),
    )
    test_session.add(coupon)
    test_session.commit()
    with pytest.raises(ValueError, match="Mã giảm giá đã hết hạn."):
        dao.save_coupon_for_user(sample_user, coupon.id)

def test_save_coupon_failed_out_of_stock(test_session, sample_user):
    coupon = Coupon(
        name="Giam gia mua mua",
        code="SALE123",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=10,
        show_public=True,
        status=CouponStatus.ACTIVE,
        quantity=0,
        active=True,
        start_date=get_past(30),
        end_date=get_future(30),
    )
    test_session.add(coupon)
    test_session.commit()

    with pytest.raises(ValueError, match="Mã giảm giá đã hết lượt."):
        dao.save_coupon_for_user(sample_user, coupon.id)

def test_save_coupon_failed_already_saved(test_session, sample_user):
    coupon = Coupon(
        name="Giam gia mua mua",
        code="SALE123",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=10,
        show_public=True,
        status=CouponStatus.ACTIVE,
        quantity=10,
        active=True,
        start_date=get_past(30),
        end_date=get_future(30),
    )
    test_session.add(coupon)
    test_session.commit()

    dao.save_coupon_for_user(sample_user, coupon.id)

    with pytest.raises(ValueError, match="Bạn đã lưu mã này rồi."):
        dao.save_coupon_for_user(sample_user, coupon.id)

def test_save_coupon_when_not_started(test_session, sample_user):
    coupon = Coupon(
        name="Giam gia mua mua",
        code="SALE123",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=10,
        show_public=True,
        status=CouponStatus.ACTIVE,
        quantity=10,
        active=True,
        start_date=get_future(10),
        end_date=get_future(30),
    )
    test_session.add(coupon)
    test_session.commit()

    user_coupon = dao.save_coupon_for_user(sample_user, coupon.id)
    assert user_coupon.user_id == sample_user.id

def test_apply_coupon_success(test_session, sample_user, sample_product):
    coupon = Coupon(
        name="Giam gia mua mua",
        code="SALE123",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=10,
        show_public=True,
        status=CouponStatus.ACTIVE,
        quantity=10,
        active=True,
        start_date=get_past(10),
        end_date=get_future(30),
    )
    test_session.add(coupon)
    uc = UserCoupon(
        user_id=sample_user.id,
        coupon_id=coupon.id,
        is_used=False,
    )
    test_session.add(uc)

    cart = Cart(
        user_id=sample_user.id
    )
    test_session.add(cart)
    item=CartItem(
        cart=cart,
        product_id=sample_product.id,
        quantity=1,
        price= sample_product.price
    )
    test_session.add(item)
    test_session.commit()

    result = dao.validate_selected_coupon_for_cart(sample_user, coupon.id, [sample_product.id])
    assert result["discount_amount"] == 200000
    assert result["code"] == "SALE123"

def test_apply_coupon_invalid_category(test_session, sample_user, sample_product):
    category = Category(name="Giay", active=True)
    test_session.add(category)
    test_session.commit()

    coupon = Coupon(
        name="Giam gia mua mua",
        code="SALE123",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=10,
        show_public=True,
        status=CouponStatus.ACTIVE,
        quantity=10,
        active=True,
        start_date=get_past(10),
        end_date=get_future(30),
        apply_type=CouponApplyType.CATEGORY
    )
    test_session.add(coupon)
    test_session.flush()
    test_session.add(CouponCategory(coupon_id=coupon.id, category_id=category.id))
    test_session.add(UserCoupon(user_id=sample_user.id, coupon_id=coupon.id, is_used=False))
    cart = Cart(
        user_id=sample_user.id
    )
    test_session.add(cart)
    item = CartItem(
        cart=cart,
        product_id=sample_product.id,
        quantity=1,
        price=sample_product.price
    )
    test_session.add(item)
    test_session.commit()

    with pytest.raises(ValueError, match="Mã không áp dụng cho sản phẩm đã chọn"):
        dao.validate_selected_coupon_for_cart(sample_user, coupon.id, [sample_product.id])

def test_apply_coupon_min_order_value_not_reached(test_session, sample_user, sample_product):
    coupon = Coupon(
        name="Giam gia mua mua",
        code="SALE123",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=10,
        show_public=True,
        status=CouponStatus.ACTIVE,
        min_order_value=500000,
        quantity=10,
        active=True,
        start_date=get_past(10),
        end_date=get_future(30)
    )
    test_session.add(coupon)
    test_session.add(UserCoupon(user_id=sample_user.id, coupon_id=coupon.id, is_used=False))

    cart = Cart(user_id=sample_user.id)
    test_session.add(cart)
    test_session.add(CartItem(
        cart=cart,
        product_id=sample_product.id,
        quantity=1,
        price=sample_product.price
    ))
    test_session.commit()
    with pytest.raises(ValueError, match="Chưa đạt giá trị đơn tối thiểu để áp dụng mã"):
        dao.validate_selected_coupon_for_cart(sample_user, coupon.id, [sample_product.id])

def test_apply_coupon_no_product_selected(test_session, sample_user):
    with pytest.raises(ValueError, match="Vui lòng chọn sản phẩm trước khi áp dụng mã giảm giá"):
        dao.validate_selected_coupon_for_cart(sample_user, 1, [])

def test_apply_coupon_percentage_with_max_limit(test_session, sample_user, sample_product):
    sample_product.price = 1000000
    coupon = Coupon(
        name="Giam gia mua mua",
        code="SALE123",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=10,
        show_public=True,
        status=CouponStatus.ACTIVE,
        min_order_value=500000,
        quantity=10,
        active=True,
        start_date=get_past(10),
        end_date=get_future(30)
    )
    test_session.add(coupon)
    test_session.add(UserCoupon(user_id=sample_user.id, coupon_id=coupon.id, is_used=False))
    cart = Cart(user_id=sample_user.id)
    test_session.add(cart)
    test_session.add(CartItem(cart=cart, product_id=sample_product.id, quantity=1, price=1000000))
    test_session.commit()

    result = dao.validate_selected_coupon_for_cart(sample_user, coupon.id, [sample_product.id])
    assert result["discount_amount"] == 100000

def test_apply_coupon_fixed_not_exceed_subtotal(test_session, sample_user, sample_product):
    sample_product.price = 30000
    coupon = Coupon(
        name="Giam gia mua mua",
        code="SALE123",
        discount_kind=DiscountKind.FIXED,
        discount_value=100000,
        show_public=True,
        status=CouponStatus.ACTIVE,
        min_order_value=5000,
        quantity=10,
        active=True,
        start_date=get_past(10),
        end_date=get_future(30)
    )
    test_session.add(coupon)
    test_session.add(UserCoupon(user_id=sample_user.id, coupon_id=coupon.id, is_used=False))
    cart = Cart(user_id=sample_user.id)
    test_session.add(cart)
    test_session.add(CartItem(cart=cart, product_id=sample_product.id, quantity=1, price=30000))
    test_session.commit()

    result = dao.validate_selected_coupon_for_cart(sample_user, coupon.id, [sample_product.id])
    assert result["discount_amount"] == 30000

