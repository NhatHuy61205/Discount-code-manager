import pytest
from datetime import datetime, timedelta
from app.test.test_base import test_session, test_app
from app import dao
from app.models import Coupon, DiscountKind, CouponStatus, User, \
    Category, Product, UserCoupon, Cart, CartItem, CouponCategory, CouponApplyType, Order, OrderStatus


def get_past(day=1): return datetime.now() - timedelta(days=day)
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

@pytest.fixture
def user_cart_with_item(test_session, sample_user, sample_product):
    cart = dao.get_or_create_cart(sample_user)
    item = CartItem(
        cart_id=cart.id,
        product_id=sample_product.id,
        quantity=2,
        price = sample_product.price
    )
    test_session.add(item)
    test_session.commit()
    return cart, item

@pytest.fixture
def valid_coupon(test_session, sample_user):
    coupon = Coupon(
        name="Giam gia 30/4",
        code="SALE304",
        discount_kind= DiscountKind.FIXED,
        discount_value= 50000,
        min_order_value= 100000,
        quantity= 10,
        start_date = get_past(10),
        end_date = get_future(10),
        status = CouponStatus.ACTIVE,
        apply_type = CouponApplyType.ALL_PRODUCT,
        active=True
    )
    test_session.add(coupon)
    test_session.flush()

    user_coupon = UserCoupon(
        user_id=sample_user.id,
        coupon_id=coupon.id,
        is_used = False,
    )
    test_session.add(user_coupon)
    test_session.commit()
    return coupon

def test_create_order_success_no_coupon(test_session, sample_user, user_cart_with_item, sample_product):
    cart, item = user_cart_with_item
    initial_stock = sample_product.stock_quantity

    order = dao.create_order_from_checkout(
        user=sample_user,
        selected_product_ids=[sample_product.id]
    )
    assert order is not None
    assert order.status == OrderStatus.PLACED
    assert order.total_amount == 2 * 200000
    assert order.discount_amount == 0

    assert sum(item.quantity for item in order.order_items) == 2

    test_session.refresh(sample_product)
    assert sample_product.stock_quantity == initial_stock - 2

    cart_items = dao.get_cart_items_by_user(sample_user)
    assert len(cart_items) == 0

def test_create_order_success_with_coupon(test_session, sample_user, user_cart_with_item, sample_product, valid_coupon):
    order = dao.create_order_from_checkout(
        user=sample_user,
        selected_product_ids=[sample_product.id],
        coupon_id=valid_coupon.id
    )
    assert order.discount_amount == 50000
    assert order.final_amount == (2 * 200000) - 50000

    user_coupon = UserCoupon.query.filter_by(user_id=sample_user.id, coupon_id=valid_coupon.id).first()
    assert user_coupon.is_used is True
    assert valid_coupon.used_count == 1

# không chọn sản phẩm
def test_create_order_fail_empty_selection(test_session, sample_user):
    with pytest.raises(ValueError, match="Không có sản phẩm nào để đặt hàng"):
        dao.create_order_from_checkout(user=sample_user, selected_product_ids=[])

# Không đủ tồn kho
def test_create_order_fail_insufficient_stock(test_session, sample_user, user_cart_with_item, sample_product):
    sample_product.stock_quantity = 0
    test_session.commit()

    with pytest.raises(ValueError, match=f"Sản phẩm {sample_product.name} không đủ tồn kho"):
        dao.create_order_from_checkout(user=sample_user, selected_product_ids=[sample_product.id])

# mã giảm giá đã được sử dụng
def test_create_order_fail_coupon_already_used(test_session, sample_user, user_cart_with_item, sample_product, valid_coupon):
    user_coupon = UserCoupon.query.filter_by(user_id=sample_user.id, coupon_id=valid_coupon.id).first()
    user_coupon.is_used = True
    test_session.commit()
    with pytest.raises(ValueError, match="Mã đã được sử dụng"):
        dao.create_order_from_checkout(user=sample_user, selected_product_ids=[sample_product.id], coupon_id=valid_coupon.id)

# xem lịch sử đơn hàng
def test_get_orders_history(test_session, sample_user, user_cart_with_item, sample_product):
    dao.create_order_from_checkout(user=sample_user, selected_product_ids=[sample_product.id])

    orders = dao.get_orders_by_user(sample_user)
    assert len(orders) >= 1
    if len(orders) > 1:
        assert orders[0].created_at >= orders[1].created_at

# giảm giá không hơn tổng số tiền
def test_order_final_amount_non_negative(test_session, sample_user, sample_product, user_cart_with_item):
    coupon = Coupon(
        name="Giam gia 30/4",
        code="SALE304",
        discount_kind= DiscountKind.FIXED,
        discount_value= 500000000,
        min_order_value= 100000,
        quantity= 10,
        start_date = get_past(10),
        end_date = get_future(10),
        status = CouponStatus.ACTIVE,
        apply_type = CouponApplyType.ALL_PRODUCT,
        active=True
    )
    test_session.add(coupon)
    test_session.flush()
    test_session.add(UserCoupon(user_id=sample_user.id, coupon_id=coupon.id, is_used=False))

    cart, item = user_cart_with_item

    order = dao.create_order_from_checkout(
        user=sample_user,
        selected_product_ids=[sample_product.id],
        coupon_id=coupon.id,
    )

    assert order.final_amount == 0
    assert order.discount_amount == 200000 * 2

# Người dùng chưa đăng nhập
def test_create_order_no_user(test_session):
    with pytest.raises(Exception):
        dao.create_order_from_checkout(user=None, selected_product_ids=[1])