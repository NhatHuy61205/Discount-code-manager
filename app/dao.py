import hashlib
import math
import os
import random
import re
import string
import uuid
from datetime import datetime

from flask import url_for
from sqlalchemy import text, func, desc
from werkzeug.utils import secure_filename

from app import app, db
from app import login
from app.models import User, CouponStatus, CouponCondition, Product, CouponApplyType, DiscountKind, Coupon, Category, \
    CouponCategory, CouponProduct, CouponTargetType, Cart, UserCoupon, UserAddress, Address, OrderItem, Order, \
    OrderStatus, ProductDetail, CouponType, ProductImage, CartItem, UserRole

MAX_DISCOUNT_RATE = 0.5


# USER

def auth_user(username, password):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    return User.query.filter(
        User.username == username,
        User.password == password,
        User.active == True
    ).first()


def get_user_by_username(username):
    return User.query.filter(User.username == username).first()


def get_user_by_email(email):
    return User.query.filter(User.email == email).first()


def get_user_by_phone(phone):
    return User.query.filter(User.phone == phone).first()


def add_user(name, username, email, phone, address, password):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()

    user = User(
        name=name,
        username=username,
        email=email,
        phone=phone,
        address=address,
        password=password
    )

    db.session.add(user)
    db.session.commit()

    return user


@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def admin_reset_user_password(user_id, new_password=None):
    user = User.query.get(user_id)

    if not user:
        raise ValueError("Người dùng không tồn tại")

    if not new_password:
        chars = string.ascii_letters + string.digits
        new_password = "".join(random.choice(chars) for _ in range(10)) + "@1"

    if len(new_password) < 8:
        raise ValueError("Mật khẩu mới không hợp lệ")

    user.password = hashlib.md5(new_password.encode("utf-8")).hexdigest()
    db.session.commit()

    return new_password


def validate_user_form_data_for_admin(
        name,
        username,
        email,
        phone,
        address,
        password,
        user_id=None,
        require_password=True
):
    name = (name or "").strip()
    username = (username or "").strip()
    email = (email or "").strip().lower()
    phone = (phone or "").strip()
    address = (address or "").strip()
    password = password or ""

    if not all([name, username, email, address]):
        raise ValueError("Vui lòng nhập đầy đủ thông tin")

    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.fullmatch(email_pattern, email):
        raise ValueError("Email không đúng định dạng")
    if password:
        if len(password) < 8:
            raise ValueError("Mật khẩu phải tối thiểu 8 ký tự")

        if not re.search(r"[A-Za-z]", password):
            raise ValueError("Mật khẩu phải chứa chữ")

        if not re.search(r"\d", password):
            raise ValueError("Mật khẩu phải chứa số")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Mật khẩu phải chứa ký tự đặc biệt")

    if phone and not re.fullmatch(r"\d{10}", phone):
        raise ValueError("Số điện thoại phải đúng 10 chữ số")

    existed_username = User.query.filter(
        User.username == username,
        User.id != user_id if user_id else True
    ).first()
    if existed_username:
        raise ValueError("Tên đăng nhập đã tồn tại")

    existed_email = User.query.filter(
        User.email == email,
        User.id != user_id if user_id else True
    ).first()
    if existed_email:
        raise ValueError("Email đã tồn tại")

    if phone:
        existed_phone = User.query.filter(
            User.phone == phone,
            User.id != user_id if user_id else True
        ).first()
        if existed_phone:
            raise ValueError("Số điện thoại đã được sử dụng")


def register_user(name, username, email, phone, address, password, confirm):
    name = (name or "").strip()
    username = (username or "").strip()
    email = (email or "").strip().lower()
    phone = (phone or "").strip()
    address = (address or "").strip()
    password = password or ""
    confirm = confirm or ""

    validate_user_form_data_for_admin(
        name=name,
        username=username,
        email=email,
        phone=phone,
        address=address,
        password=password,
        user_id=None,
        require_password=True
    )

    if password != confirm:
        raise ValueError("Mật khẩu không khớp")

    password = hashlib.md5(password.encode("utf-8")).hexdigest()

    user = User(
        name=name,
        username=username,
        email=email,
        phone=phone,
        address=address,
        password=password
    )

    db.session.add(user)
    db.session.commit()
    return user


def get_default_address_for_user(user):
    sql = text("""
            SELECT a.id, a.recipient_name, a.phone, a.address_line
            FROM address a
            JOIN user_address ua ON ua.address_id = a.id
            WHERE ua.user_id = :user_id AND a.active = true
            ORDER BY ua.is_default DESC, a.id ASC
            LIMIT 1
        """)

    row = db.session.execute(sql, {"user_id": user.id}).mappings().first()

    if row:
        return {
            "id": row["id"],
            "recipient_name": row["recipient_name"],
            "phone": row["phone"],
            "address_line": row["address_line"],
            "is_default": True
        }

    if user.address:
        return {
            "id": None,
            "recipient_name": user.name,
            "phone": user.phone,
            "address_line": user.address,
            "is_default": True
        }

    return None


def get_addresses_by_user(user):
    sql = text("""
            SELECT a.id, a.recipient_name, a.phone, a.address_line, ua.is_default
            FROM address a
            JOIN user_address ua ON ua.address_id = a.id
            WHERE ua.user_id = :user_id AND a.active = true
            ORDER BY ua.is_default DESC, a.id DESC
        """)

    rows = db.session.execute(sql, {"user_id": user.id}).mappings().all()

    return [
        {
            "id": row["id"],
            "recipient_name": row["recipient_name"],
            "phone": row["phone"],
            "address_line": row["address_line"],
            "is_default": row["is_default"]
        }
        for row in rows
    ]


def update_user_address(user, address_id, recipient_name, phone, address_line, set_as_default=False):
    recipient_name = (recipient_name or "").strip()
    phone = (phone or "").strip()
    address_line = (address_line or "").strip()

    if not recipient_name:
        raise ValueError("Vui lòng nhập họ và tên")

    if not phone:
        raise ValueError("Vui lòng nhập số điện thoại")

    if not re.fullmatch(r"\d{10}", phone):
        raise ValueError("Số điện thoại phải đúng 10 chữ số")

    if not address_line:
        raise ValueError("Vui lòng nhập địa chỉ")

    user_address = UserAddress.query.filter_by(
        user_id=user.id,
        address_id=address_id
    ).first()

    if not user_address:
        raise ValueError("Địa chỉ không tồn tại hoặc không thuộc về bạn")

    address = Address.query.get(address_id)

    if not address or not address.active:
        raise ValueError("Địa chỉ không hợp lệ")

    address.recipient_name = recipient_name
    address.phone = phone
    address.address_line = address_line

    if set_as_default:
        UserAddress.query.filter_by(user_id=user.id).update(
            {"is_default": False},
            synchronize_session=False
        )
        user_address.is_default = True

    db.session.commit()

    return {
        "id": address.id,
        "recipient_name": address.recipient_name,
        "phone": address.phone,
        "address_line": address.address_line,
        "is_default": user_address.is_default
    }


def create_user_address(user, recipient_name, phone, address_line, set_as_default=False):
    recipient_name = (recipient_name or "").strip()
    phone = (phone or "").strip()
    address_line = (address_line or "").strip()

    if not recipient_name:
        raise ValueError("Vui lòng nhập họ và tên")

    if not phone:
        raise ValueError("Vui lòng nhập số điện thoại")

    if not re.fullmatch(r"\d{10}", phone):
        raise ValueError("Số điện thoại phải đúng 10 chữ số")

    if not address_line:
        raise ValueError("Vui lòng nhập địa chỉ")

    has_address = UserAddress.query.filter_by(user_id=user.id).first()

    if not has_address:
        set_as_default = True

    address = Address(
        name=recipient_name,
        recipient_name=recipient_name,
        phone=phone,
        address_line=address_line,
        active=True
    )

    db.session.add(address)
    db.session.flush()

    if set_as_default:
        UserAddress.query.filter_by(user_id=user.id).update(
            {"is_default": False},
            synchronize_session=False
        )

    user_address = UserAddress(
        user_id=user.id,
        address_id=address.id,
        is_default=set_as_default
    )

    db.session.add(user_address)
    db.session.commit()

    return {
        "id": address.id,
        "recipient_name": address.recipient_name,
        "phone": address.phone,
        "address_line": address.address_line,
        "is_default": user_address.is_default
    }


# PAGE
def paginate_query(query, page=1, page_size=None):
    page = int(page or 1)
    if page < 1:
        page = 1

    page_size = page_size or app.config["PAGE_SIZE"]

    total = query.count()
    pages = math.ceil(total / page_size) if total > 0 else 1

    if page > pages:
        page = pages

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": items,
        "page": page,
        "pages": pages,
        "total": total,
        "page_size": page_size,
        "has_next": page < pages,
        "has_prev": page > 1
    }


# COUPON
def get_remaining_quantity(coupon):
    saved_count = UserCoupon.query.filter_by(coupon_id=coupon.id).count()
    return max((coupon.quantity or 0) - saved_count, 0)


def get_usage_text(coupon):
    saved_count = UserCoupon.query.filter_by(coupon_id=coupon.id).count()
    return f"{saved_count}/{coupon.quantity or 0}"


def get_coupon_condition(coupon):
    """
    Trả về tình trạng của mã giảm giá:
    - UPCOMING: chưa tới ngày bắt đầu
    - AVAILABLE: đang dùng được
    - OUT_OF_STOCK: hết lượt
    - EXPIRED: hết hạn
    - DISABLED: bị tắt
    """

    now = datetime.now()

    if coupon.status == CouponStatus.INACTIVE or coupon.active is False:
        return CouponCondition.DISABLED

    if coupon.end_date and coupon.end_date < now:
        return CouponCondition.EXPIRED

    if coupon.start_date and coupon.start_date > now:
        return CouponCondition.UPCOMING

    saved_count = UserCoupon.query.filter_by(coupon_id=coupon.id).count()

    if coupon.quantity is not None and saved_count >= (coupon.quantity or 0):
        return CouponCondition.OUT_OF_STOCK

    return CouponCondition.AVAILABLE


def get_valid_coupons():
    now = datetime.now()

    coupons = Coupon.query.filter(
        Coupon.active == True,
        Coupon.status == CouponStatus.ACTIVE,
        Coupon.start_date <= now,
        Coupon.end_date >= now
    ).all()

    valid_coupons = []

    for coupon in coupons:
        saved_count = UserCoupon.query.filter_by(coupon_id=coupon.id).count()

        if coupon.quantity is not None and saved_count >= (coupon.quantity or 0):
            continue

        valid_coupons.append(coupon)

    return valid_coupons


def is_coupon_applicable_to_product(coupon, product):
    if coupon.apply_type == CouponApplyType.ALL_PRODUCT:
        return True

    if coupon.apply_type == CouponApplyType.CATEGORY:
        cate_ids = [cc.category_id for cc in coupon.coupon_categories]
        return product.cate_id in cate_ids

    if coupon.apply_type == CouponApplyType.PRODUCT:
        product_ids = [cp.product_id for cp in coupon.coupon_products]
        return product.id in product_ids

    return False


def calculate_coupon_discount_for_product(coupon, product):
    base_amount = product.price
    max_allowed_discount = base_amount * MAX_DISCOUNT_RATE

    if coupon.discount_kind == DiscountKind.PERCENTAGE:
        discount = base_amount * (coupon.discount_value / 100)

        if coupon.max_discount_value:
            discount = min(discount, coupon.max_discount_value)
    else:
        discount = coupon.discount_value

    return min(discount, max_allowed_discount)


def get_best_coupon_for_product(product):
    coupons = get_valid_coupons()

    best_coupon = None
    best_discount = 0

    for coupon in coupons:
        if not is_coupon_applicable_to_product(coupon, product):
            continue

        discount = calculate_coupon_discount_for_product(coupon, product)

        if discount > best_discount:
            best_discount = discount
            best_coupon = coupon

    return best_coupon, best_discount


def get_used_coupons(user):
    return UserCoupon.query.filter_by(
        user_id=user.id,
        is_used=True
    ).all()


def get_public_coupons_for_user(user):
    now = datetime.now()

    owned_coupon_ids = [
        uc.coupon_id for uc in UserCoupon.query.filter_by(user_id=user.id).all()
    ]

    coupons = Coupon.query.filter(
        Coupon.active == True,
        Coupon.status == CouponStatus.ACTIVE,
        Coupon.show_public == True,
        Coupon.start_date <= now,
        Coupon.end_date >= now
    ).order_by(Coupon.created_date.desc()).all()

    available_coupons = []

    for coupon in coupons:
        saved_count = UserCoupon.query.filter_by(coupon_id=coupon.id).count()

        if coupon.quantity is not None and saved_count >= (coupon.quantity or 0):
            continue

        if coupon.id in owned_coupon_ids:
            continue

        available_coupons.append(coupon)

    return available_coupons


def get_my_coupons(user):
    user_coupons = UserCoupon.query.filter_by(
        user_id=user.id,
        is_used=False
    ) \
        .join(Coupon, UserCoupon.coupon_id == Coupon.id) \
        .order_by(UserCoupon.id.desc()) \
        .all()

    return user_coupons


def save_coupon_for_user(user, coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)

    now = datetime.now()

    if not coupon.active or coupon.status != CouponStatus.ACTIVE:
        raise ValueError("Mã giảm giá hiện không khả dụng.")

    if not coupon.show_public:
        raise ValueError("Mã này không hiển thị công khai.")

    if coupon.start_date and coupon.start_date > now:
        raise ValueError("Mã giảm giá chưa tới thời gian sử dụng.")

    if coupon.end_date and coupon.end_date < now:
        raise ValueError("Mã giảm giá đã hết hạn.")

    saved_count = UserCoupon.query.filter_by(coupon_id=coupon.id).count()

    if coupon.quantity is not None and saved_count >= (coupon.quantity or 0):
        raise ValueError("Mã giảm giá đã hết lượt.")

    existed = UserCoupon.query.filter_by(
        user_id=user.id,
        coupon_id=coupon.id
    ).first()

    if existed:
        raise ValueError("Bạn đã lưu mã này rồi.")

    user_coupon = UserCoupon(
        user_id=user.id,
        coupon_id=coupon.id,
        is_used=False
    )

    db.session.add(user_coupon)
    db.session.commit()

    return user_coupon


def get_days_remaining(coupon):
    if not coupon.end_date:
        return None

    now = datetime.now()
    delta = coupon.end_date - now
    return delta.days


def get_apply_type_text(coupon):
    if coupon.apply_type == CouponApplyType.ALL_PRODUCT:
        return "Áp dụng toàn shop"

    if coupon.apply_type == CouponApplyType.CATEGORY:
        return "Áp dụng theo ngành hàng"

    if coupon.apply_type == CouponApplyType.PRODUCT:
        return "Áp dụng theo sản phẩm"

    return "Không xác định"


# CART
def get_or_create_cart(user):
    cart = Cart.query.filter_by(user_id=user.id).first()

    if not cart:
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()

    return cart


def stats_cart_db(cart):
    if not cart or not cart.cart_items:
        return {
            "total_quantity": 0,
            "total_amount": 0,
            "total_items": 0
        }

    total_quantity = sum(item.quantity for item in cart.cart_items)
    total_amount = sum(item.quantity * item.price for item in cart.cart_items)
    total_items = len(cart.cart_items)

    return {
        "total_quantity": total_quantity,
        "total_amount": total_amount,
        "total_items": total_items
    }


def get_cart_items_by_user(user):
    cart = get_or_create_cart(user)
    return cart.cart_items


def get_available_my_coupons_for_cart(user, selected_product_ids):
    if not selected_product_ids:
        raise ValueError("Vui lòng chọn sản phẩm trước khi chọn mã giảm giá")

    cart_items = get_cart_items_by_user(user)
    selected_product_ids = {int(pid) for pid in selected_product_ids}

    selected_items = [
        item for item in cart_items
        if item.product_id in selected_product_ids
    ]

    if not selected_items:
        raise ValueError("Vui lòng chọn sản phẩm trước khi chọn mã giảm giá")

    now = datetime.now()
    result = []

    user_coupons = UserCoupon.query.filter_by(user_id=user.id) \
        .join(Coupon, UserCoupon.coupon_id == Coupon.id) \
        .order_by(UserCoupon.id.desc()) \
        .all()

    selected_subtotal = sum(item.price * item.quantity for item in selected_items)

    for uc in user_coupons:
        coupon = uc.coupon
        is_usable = True
        invalid_reason = ""

        applicable_items = [
            item for item in selected_items
            if is_coupon_applicable_to_product(coupon, item.product)
        ]
        applicable_subtotal = sum(item.price * item.quantity for item in applicable_items)

        if uc.is_used:
            is_usable = False
            invalid_reason = "Mã đã được sử dụng"
        elif not coupon.active or coupon.status != CouponStatus.ACTIVE:
            is_usable = False
            invalid_reason = "Mã hiện không khả dụng"
        elif coupon.start_date and coupon.start_date > now:
            is_usable = False
            invalid_reason = "Mã chưa tới thời gian sử dụng"
        elif coupon.end_date and coupon.end_date < now:
            is_usable = False
            invalid_reason = "Mã đã hết hạn"
        else:
            saved_count = UserCoupon.query.filter_by(coupon_id=coupon.id).count()

            if coupon.quantity is not None and saved_count >= (coupon.quantity or 0):
                is_usable = False
                invalid_reason = "Mã đã hết lượt"
            elif not applicable_items:
                is_usable = False
                invalid_reason = "Mã không áp dụng cho sản phẩm đã chọn"
            elif selected_subtotal < (coupon.min_order_value or 0):
                is_usable = False
                invalid_reason = "Chưa đạt giá trị đơn tối thiểu"

        discount_amount = 0
        if is_usable:
            max_allowed_discount = applicable_subtotal * MAX_DISCOUNT_RATE

            if coupon.discount_kind == DiscountKind.PERCENTAGE:
                discount_amount = applicable_subtotal * (coupon.discount_value / 100)

                if coupon.max_discount_value:
                    discount_amount = min(discount_amount, coupon.max_discount_value)
            else:
                discount_amount = coupon.discount_value

            discount_amount = min(discount_amount, max_allowed_discount)

        result.append({
            "user_coupon_id": uc.id,
            "coupon_id": coupon.id,
            "code": coupon.code,
            "name": coupon.name,
            "description": coupon.description,
            "discount_kind": coupon.discount_kind.value,
            "discount_value": coupon.discount_value,
            "max_discount_value": coupon.max_discount_value,
            "min_order_value": coupon.min_order_value or 0,
            "apply_type": coupon.apply_type.value,
            "apply_type_text": get_apply_type_text(coupon),
            "end_date": coupon.end_date.strftime("%d/%m/%Y %H:%M") if coupon.end_date else "",
            "discount_amount": round(discount_amount, 2),
            "is_usable": is_usable,
            "invalid_reason": invalid_reason
        })

    result.sort(key=lambda x: (
        not x["is_usable"],
        -x["discount_amount"]
    ))

    return result


def validate_selected_coupon_for_cart(user, coupon_id, selected_product_ids):
    if not selected_product_ids:
        raise ValueError("Vui lòng chọn sản phẩm trước khi áp dụng mã giảm giá")

    cart_items = get_cart_items_by_user(user)
    selected_product_ids = {int(pid) for pid in selected_product_ids}

    selected_items = [
        item for item in cart_items
        if item.product_id in selected_product_ids
    ]

    if not selected_items:
        raise ValueError("Vui lòng chọn sản phẩm trước khi áp dụng mã giảm giá")

    user_coupon = UserCoupon.query.filter_by(
        user_id=user.id,
        coupon_id=coupon_id
    ).first()

    if not user_coupon:
        raise ValueError("Bạn không sở hữu mã giảm giá này")

    coupon = user_coupon.coupon
    now = datetime.now()

    if user_coupon.is_used:
        raise ValueError("Mã đã được sử dụng")

    if not coupon.active or coupon.status != CouponStatus.ACTIVE:
        raise ValueError("Mã hiện không khả dụng")

    if coupon.start_date and coupon.start_date > now:
        raise ValueError("Mã chưa tới thời gian sử dụng")

    if coupon.end_date and coupon.end_date < now:
        raise ValueError("Mã đã hết hạn")

    saved_count = UserCoupon.query.filter_by(coupon_id=coupon.id).count()
    if coupon.quantity is not None and saved_count >= (coupon.quantity or 0):
        raise ValueError("Mã đã hết lượt")

    applicable_items = [
        item for item in selected_items
        if is_coupon_applicable_to_product(coupon, item.product)
    ]

    if not applicable_items:
        raise ValueError("Mã không áp dụng cho sản phẩm đã chọn")

    selected_subtotal = sum(item.price * item.quantity for item in selected_items)
    applicable_subtotal = sum(item.price * item.quantity for item in applicable_items)

    if selected_subtotal < (coupon.min_order_value or 0):
        raise ValueError("Chưa đạt giá trị đơn tối thiểu để áp dụng mã")

    max_allowed_discount = applicable_subtotal * MAX_DISCOUNT_RATE

    if coupon.discount_kind == DiscountKind.PERCENTAGE:
        discount_amount = applicable_subtotal * (coupon.discount_value / 100)

        if coupon.max_discount_value:
            discount_amount = min(discount_amount, coupon.max_discount_value)
    else:
        discount_amount = coupon.discount_value

    discount_amount = min(discount_amount, max_allowed_discount)

    return {
        "coupon_id": coupon.id,
        "code": coupon.code,
        "discount_amount": round(discount_amount, 2)
    }


def update_cart_item_quantity(user, product_id, quantity):
    cart = get_or_create_cart(user)
    product = get_product_by_id(product_id)

    quantity = int(quantity or 1)

    if quantity <= 0:
        raise ValueError("Số lượng phải lớn hơn 0")

    if quantity > product.stock_quantity:
        raise ValueError(f"Chỉ còn {product.stock_quantity} sản phẩm trong kho")

    item = next(
        (i for i in cart.cart_items if i.product_id == product.id),
        None
    )

    if not item:
        raise LookupError("Sản phẩm không có trong giỏ hàng")

    item.quantity = quantity
    db.session.commit()

    return stats_cart_db(cart)


def delete_cart_item_by_product(user, product_id):
    cart = get_or_create_cart(user)

    item = next(
        (i for i in cart.cart_items if i.product_id == product_id),
        None
    )

    if not item:
        raise LookupError("Sản phẩm không có trong giỏ hàng")

    db.session.delete(item)
    db.session.commit()

    return stats_cart_db(cart)


# PRODUCT

def get_active_products(page=1, q=None):
    query = Product.query.filter(Product.active == True)

    if q:
        keyword = f"%{q.strip()}%"
        query = query.outerjoin(Product.product_detail).outerjoin(Product.category).filter(
            (Product.name.ilike(keyword)) |
            (ProductDetail.description.ilike(keyword)) |
            (Category.name.ilike(keyword))
        )

    query = query.order_by(Product.id.desc())
    return paginate_query(query, page=page)


def add_product_to_cart(user, product_id, quantity=1):
    cart = get_or_create_cart(user)
    product = get_product_by_id(product_id)

    quantity = int(quantity or 1)

    if quantity <= 0:
        raise ValueError("Số lượng phải lớn hơn 0")

    if product.stock_quantity <= 0:
        raise ValueError("Sản phẩm đã hết hàng")

    item = next(
        (i for i in cart.cart_items if i.product_id == product.id),
        None
    )

    if item:
        if item.quantity + quantity > product.stock_quantity:
            raise ValueError(f"Chỉ còn {product.stock_quantity} sản phẩm trong kho")

        item.quantity += quantity
    else:
        if quantity > product.stock_quantity:
            raise ValueError(f"Chỉ còn {product.stock_quantity} sản phẩm trong kho")

        item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price
        )
        db.session.add(item)

    db.session.commit()
    return stats_cart_db(cart)


# recommend
def get_recommended_products(page=1):
    query = Product.query.filter_by(active=True).order_by(Product.id.desc())
    return paginate_query(query, page=page)


def get_product_by_id(product_id):
    return Product.query.get_or_404(product_id)


def get_suggested_products(limit=10):
    return Product.query.filter_by(active=True).limit(limit).all()


# ========= ADMIN =========
def parse_datetime_local(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d/%m/%Y %H:%M")
    except ValueError:
        return None


def to_int_list(values):
    result = []
    for v in values:
        try:
            result.append(int(v))
        except (TypeError, ValueError):
            continue
    return result


def get_coupon_form_data(request_form, coupon=None):
    return {
        "name": request_form.get("name", coupon.name if coupon else "").strip(),
        "code": request_form.get("code", coupon.code if coupon else "").strip().upper(),
        "description": request_form.get("description", coupon.description if coupon else "").strip(),
        "discount_kind": request_form.get(
            "discount_kind",
            coupon.discount_kind.value if coupon and coupon.discount_kind else "fixed"
        ),
        "show_public": request_form.get(
            "show_public",
            "1" if coupon and coupon.show_public else ""
        ),
        "discount_value": request_form.get(
            "discount_value",
            coupon.discount_value if coupon else ""
        ),
        "max_discount_value": request_form.get(
            "max_discount_value",
            coupon.max_discount_value if coupon and coupon.max_discount_value is not None else ""
        ),
        "min_order_value": request_form.get(
            "min_order_value",
            coupon.min_order_value if coupon else ""
        ),
        "quantity": request_form.get(
            "quantity",
            coupon.quantity if coupon else ""
        ),
        "used_count": coupon.used_count if coupon else 0,
        "start_date": (
            coupon.start_date.strftime("%d/%m/%Y %H:%M")
            if coupon and coupon.start_date else request_form.get("start_date", "")
        ),
        "end_date": request_form.get(
            "end_date",
            coupon.end_date.strftime("%d/%m/%Y %H:%M") if coupon and coupon.end_date else ""
        ),
        "status": request_form.get(
            "status",
            coupon.status.name if coupon and coupon.status else "ACTIVE"
        ),
    }


def query_coupons_for_admin(args):
    query = Coupon.query

    q = args.get("q", "").strip()
    apply_type = args.get("apply_type", "").strip()
    condition = args.get("condition", "").strip()
    status = args.get("status", "").strip()
    created_date = args.get("created_date", "").strip()
    start_date = args.get("start_date", "").strip()

    if q:
        query = query.filter(
            (Coupon.name.ilike(f"%{q}%")) |
            (Coupon.code.ilike(f"%{q}%")) |
            (Coupon.description.ilike(f"%{q}%"))
        )

    if apply_type:
        query = query.filter(Coupon.apply_type == apply_type)

    if status:
        query = query.filter(Coupon.status == status)

    if created_date:
        query = query.filter(db.func.date(Coupon.created_date) == created_date)

    if start_date:
        query = query.filter(db.func.date(Coupon.start_date) == start_date)

    coupons = query.order_by(Coupon.id.desc()).all()

    if condition:
        coupons = [c for c in coupons if get_coupon_condition(c).value == condition]

    return coupons


def get_coupon_create_dependencies():
    categories = Category.query.filter_by(active=True).order_by(Category.name.asc()).all()
    products = Product.query.filter_by(active=True) \
        .order_by(Product.stock_quantity.desc(), Product.name.asc()) \
        .all()

    coupon_types = CouponType.query.order_by(CouponType.name.asc()).all()
    return categories, products, coupon_types


def parse_float_field(value, field_name, default=0):
    value = str(value or "").strip()

    if value == "":
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} phải là số hợp lệ.")


def parse_int_field(value, field_name, default=0):
    value = str(value or "").strip()

    if value == "":
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} phải là số nguyên hợp lệ.")


# Tạo mã giảm giá
def create_coupon_from_form(form):
    name = form.get("name", "").strip()
    code = form.get("code", "").strip().upper()
    description = form.get("description", "").strip()

    discount_kind_raw = form.get("discount_kind", "fixed")
    apply_scope = form.get("apply_scope", "all_product")
    target_type_raw = form.get("target_type", "all")

    max_discount_value = parse_float_field(
        form.get("max_discount_value"),
        "Giảm tối đa",
        default=None
    )

    discount_value = parse_float_field(
        form.get("discount_value"),
        "Mức giảm",
        default=0
    )

    min_order_value = parse_float_field(
        form.get("min_order_value"),
        "Giá trị đơn tối thiểu",
        default=0
    )

    quantity = parse_int_field(
        form.get("quantity"),
        "Số lượt sử dụng",
        default=0
    )

    start_date = parse_datetime_local(form.get("start_date"))
    end_date = parse_datetime_local(form.get("end_date"))
    now = datetime.now()

    usage_limit_type = form.get("usage_limit_type", "many")
    show_public = str(form.get("show_public", "")).strip() in ["1", "true", "True", "on"]

    category_ids = to_int_list(form.getlist("category_ids"))
    product_ids = to_int_list(form.getlist("product_ids"))

    if not name:
        raise ValueError("Vui lòng nhập tên mã giảm giá.")

    if not code:
        raise ValueError("Vui lòng nhập code mã giảm giá.")

    if Coupon.query.filter(Coupon.code == code).first():
        raise ValueError("Code mã giảm giá đã tồn tại.")

    if min_order_value < 0:
        raise ValueError("Giá trị đơn tối thiểu không hợp lệ.")

    if discount_value <= 0:
        raise ValueError("Mức giảm phải lớn hơn 0.")

    if discount_kind_raw == "percentage" and max_discount_value is not None and max_discount_value <= 0:
        raise ValueError("Giảm tối đa phải lớn hơn 0.")

    if discount_kind_raw == "percentage" and discount_value > 50:
        raise ValueError("Mã giảm theo % không được vượt quá 50%.")

    if quantity <= 0:
        raise ValueError("Số lượt sử dụng không hợp lệ.")

    if not start_date:
        raise ValueError("Vui lòng nhập ngày bắt đầu.")

    if not end_date:
        raise ValueError("Vui lòng nhập ngày kết thúc.")

    if start_date and start_date < now:
        raise ValueError("Thời gian bắt đầu phải lớn hơn hoặc bằng thời điểm hiện tại.")

    if end_date and end_date < now:
        raise ValueError("Thời gian kết thúc không hợp lệ.")

    if start_date and end_date and start_date > end_date:
        raise ValueError("Thời gian bắt đầu phải nhỏ hơn hoặc bằng thời gian kết thúc.")

    if apply_scope == "selected_category" and not category_ids:
        raise ValueError("Bạn phải chọn ít nhất 1 ngành hàng.")

    if apply_scope == "selected_product" and not product_ids:
        raise ValueError("Bạn phải chọn ít nhất 1 sản phẩm.")

    discount_kind = DiscountKind.PERCENTAGE if discount_kind_raw == "percentage" else DiscountKind.FIXED
    target_type = CouponTargetType.LOYAL_1Y if target_type_raw == "old_customer" else CouponTargetType.ALL

    if apply_scope == "selected_category":
        apply_type = CouponApplyType.CATEGORY
    elif apply_scope == "selected_product":
        apply_type = CouponApplyType.PRODUCT
    else:
        apply_type = CouponApplyType.ALL_PRODUCT

    usage_limit_per_user = 999999 if usage_limit_type == "many" else 1

    coupon = Coupon(
        name=name,
        code=code,
        description=description,
        discount_kind=discount_kind,
        discount_value=discount_value,
        apply_type=apply_type,
        target_type=target_type,
        status=CouponStatus.ACTIVE,
        min_order_value=min_order_value,
        quantity=quantity,
        used_count=0,
        start_date=start_date,
        end_date=end_date,
        show_public=show_public,
        usage_limit_per_user=usage_limit_per_user,
        max_discount_value=max_discount_value,
        active=True
    )

    db.session.add(coupon)
    db.session.flush()

    if apply_type == CouponApplyType.CATEGORY:
        for cate_id in category_ids:
            db.session.add(CouponCategory(coupon_id=coupon.id, category_id=cate_id))

    if apply_type == CouponApplyType.PRODUCT:
        for product_id in product_ids:
            db.session.add(CouponProduct(coupon_id=coupon.id, product_id=product_id))

    db.session.commit()
    return coupon


# Sửa mã giảm giá
def update_coupon_from_form(coupon, form_data):
    now = datetime.now()

    if not coupon.start_date or coupon.start_date <= now:
        raise ValueError("Mã giảm giá đã được phát hành nên không được chỉnh sửa.")
    name = form_data["name"]
    code = form_data["code"]
    description = form_data["description"]

    discount_kind_raw = form_data["discount_kind"]
    discount_value = parse_float_field(
        form_data["discount_value"],
        "Mức giảm",
        default=0
    )

    min_order_value = parse_float_field(
        form_data["min_order_value"],
        "Giá trị đơn tối thiểu",
        default=0
    )

    quantity = parse_int_field(
        form_data["quantity"],
        "Số lượng",
        default=0
    )
    show_public = str(form_data.get("show_public", "")).strip() in ["1", "true", "True", "on"]
    max_discount_value_raw = form_data["max_discount_value"]
    max_discount_value = parse_float_field(
        max_discount_value_raw,
        "Giảm tối đa",
        default=None
    )

    start_date_raw = (form_data.get("start_date") or "").strip()
    end_date_raw = (form_data.get("end_date") or "").strip()

    submitted_start_date = parse_datetime_local(start_date_raw)
    end_date = parse_datetime_local(end_date_raw)
    status_raw = form_data["status"]
    now = datetime.now()

    original_start_date = coupon.start_date
    can_edit_start_date = bool(original_start_date and original_start_date > now)

    if can_edit_start_date:
        start_date = submitted_start_date
    else:
        start_date = original_start_date

    if not name:
        raise ValueError("Vui lòng nhập tên mã giảm giá.")

    if not code:
        raise ValueError("Vui lòng nhập code mã giảm giá.")

    duplicate_coupon = Coupon.query.filter(
        Coupon.code == code,
        Coupon.id != coupon.id
    ).first()
    if duplicate_coupon:
        raise ValueError("Code mã giảm giá đã tồn tại.")

    if discount_value <= 0:
        raise ValueError("Mức giảm phải lớn hơn 0.")

    if discount_kind_raw == "percentage" and discount_value > 50:
        raise ValueError("Mã giảm theo % không được vượt quá 50%.")

    if discount_kind_raw == "percentage" and max_discount_value is not None and max_discount_value <= 0:
        raise ValueError("Giảm tối đa phải lớn hơn 0.")

    saved_count = UserCoupon.query.filter_by(coupon_id=coupon.id).count()
    if quantity < saved_count:
        raise ValueError("Số lượng không được nhỏ hơn số lượt đã lưu hiện tại.")

    if quantity <= 0:
        raise ValueError("Số lượng không hợp lệ.")

    if min_order_value < 0:
        raise ValueError("Giá trị đơn tối thiểu không hợp lệ.")

    if can_edit_start_date:
        if not start_date_raw:
            raise ValueError("Vui lòng nhập ngày bắt đầu.")
        if not start_date:
            raise ValueError("Ngày bắt đầu không đúng định dạng dd/mm/YYYY HH:MM.")
        if start_date < now:
            raise ValueError("Thời gian bắt đầu phải lớn hơn hoặc bằng thời điểm hiện tại.")
    else:
        original_start_date_str = original_start_date.strftime("%d/%m/%Y %H:%M") if original_start_date else ""
        submitted_start_date_str = (form_data.get("start_date") or "").strip()

        if submitted_start_date_str != original_start_date_str:
            raise ValueError("Mã giảm giá đã tới ngày bắt đầu, không được chỉnh sửa ngày bắt đầu nữa.")

    if not end_date_raw:
        raise ValueError("Vui lòng nhập ngày kết thúc.")

    if not end_date:
        raise ValueError("Ngày kết thúc không đúng định dạng dd/mm/YYYY HH:MM.")

    if end_date < now:
        raise ValueError("Thời gian kết thúc không hợp lệ.")

    if start_date and end_date and start_date > end_date:
        raise ValueError("Thời gian bắt đầu phải nhỏ hơn hoặc bằng thời gian kết thúc.")

    # if start_date and end_date and start_date > end_date:
    #    raise ValueError("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc.")

    # if start_date and start_date < now:
    #    raise ValueError("Thời gian bắt đầu phải lớn hơn hoặc bằng thời điểm hiện tại.")

    discount_kind = DiscountKind.PERCENTAGE if discount_kind_raw == "percentage" else DiscountKind.FIXED
    status = CouponStatus.INACTIVE if status_raw == "INACTIVE" else CouponStatus.ACTIVE

    coupon.name = name
    coupon.code = code
    coupon.description = description
    coupon.discount_kind = discount_kind
    coupon.discount_value = discount_value
    coupon.min_order_value = min_order_value
    coupon.quantity = quantity
    coupon.show_public = show_public
    coupon.max_discount_value = max_discount_value if discount_kind == DiscountKind.PERCENTAGE else None
    coupon.start_date = start_date
    coupon.end_date = end_date
    coupon.status = status

    db.session.commit()
    return coupon


# Xóa mã giảm giá
def delete_coupon_by_id(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)

    user_coupon_exists = UserCoupon.query.filter_by(coupon_id=coupon.id).first()
    if user_coupon_exists:
        raise ValueError("Mã đã được user lưu, không thể xóa")

    from app.models import Order
    order_exists = Order.query.filter_by(coupon_id=coupon.id).first()
    if order_exists:
        raise ValueError("Mã đã được áp dụng trong đơn hàng, không thể xóa")

    cart_exists = Cart.query.filter_by(coupon_id=coupon.id).first()
    if cart_exists:
        raise ValueError("Mã đang tồn tại trong giỏ hàng, không thể xóa")

    CouponCategory.query.filter_by(coupon_id=coupon.id).delete()
    CouponProduct.query.filter_by(coupon_id=coupon.id).delete()

    db.session.delete(coupon)
    db.session.commit()
    return coupon


# check out
def create_order_from_checkout(user, selected_product_ids, coupon_id=None, notes=None):
    selected_product_ids = [int(pid) for pid in (selected_product_ids or []) if str(pid).isdigit()]
    notes = notes or {}

    if not selected_product_ids:
        raise ValueError("Không có sản phẩm nào để đặt hàng")

    cart = get_or_create_cart(user)

    selected_items = [
        item for item in cart.cart_items
        if item.product_id in selected_product_ids
    ]

    if not selected_items:
        raise ValueError("Không tìm thấy sản phẩm hợp lệ trong giỏ hàng")

    total_amount = 0
    discount_amount = 0
    selected_coupon = None

    # Tính tổng tiền hàng + kiểm tra tồn kho
    for item in selected_items:
        if not item.product:
            raise ValueError("Có sản phẩm không tồn tại")

        if item.quantity <= 0:
            raise ValueError(f"Số lượng sản phẩm {item.product.name} không hợp lệ")

        if item.product.stock_quantity < item.quantity:
            raise ValueError(f"Sản phẩm {item.product.name} không đủ tồn kho")

        total_amount += item.price * item.quantity

    # Validate coupon lại lần cuối ở backend
    if coupon_id:
        coupon_result = validate_selected_coupon_for_cart(
            user=user,
            coupon_id=int(coupon_id),
            selected_product_ids=selected_product_ids
        )
        discount_amount = float(coupon_result.get("discount_amount", 0) or 0)
        selected_coupon = Coupon.query.get(int(coupon_id))

    final_amount = max(total_amount - discount_amount, 0)

    try:
        order = Order(
            user_id=user.id,
            coupon_id=selected_coupon.id if selected_coupon else None,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            status=OrderStatus.PLACED
        )
        db.session.add(order)
        db.session.flush()  # lấy order.id

        # Lưu chi tiết đơn hàng + trừ tồn kho
        for item in selected_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                note=(notes.get(str(item.product_id)) or "").strip() or None
            )
            db.session.add(order_item)

            item.product.stock_quantity -= item.quantity

        # Đánh dấu coupon đã dùng
        if selected_coupon:
            user_coupon = UserCoupon.query.filter_by(
                user_id=user.id,
                coupon_id=selected_coupon.id
            ).first()

            if not user_coupon:
                raise ValueError("User không sở hữu mã giảm giá này")

            if user_coupon.is_used:
                raise ValueError("Mã giảm giá này đã được sử dụng")

            user_coupon.is_used = True
            user_coupon.used_at = datetime.now()
            selected_coupon.used_count = (selected_coupon.used_count or 0) + 1

        # Xóa các sản phẩm đã đặt khỏi giỏ hàng
        for item in selected_items:
            db.session.delete(item)

        # Xóa coupon đang bám ở cart nếu có
        cart.coupon_id = None

        db.session.commit()
        return order

    except Exception:
        db.session.rollback()
        raise


# lịch sử mua hàng
def get_orders_by_user(user):
    orders = Order.query.filter_by(user_id=user.id) \
        .order_by(Order.created_at.desc()) \
        .all()

    return orders


# dashboard
def get_admin_dashboard_stats():
    now = datetime.now()

    def month_key(offset):
        month_index = now.month - 1 + offset
        year = now.year + month_index // 12
        month = month_index % 12 + 1
        return f"{year}-{month:02d}"

    month_keys = [month_key(i) for i in range(-5, 1)]

    revenue_rows = db.session.query(
        func.date_format(Order.created_at, "%Y-%m").label("month"),
        func.sum(Order.final_amount).label("revenue"),
        func.count(Order.id).label("orders")
    ).filter(
        Order.status == "completed"
    ).group_by("month").all()

    revenue_map = {
        row.month: {
            "revenue": float(row.revenue or 0),
            "orders": int(row.orders or 0)
        }
        for row in revenue_rows
    }

    top_products = db.session.query(
        Product.name.label("name"),
        func.sum(OrderItem.quantity).label("sold_quantity"),
        func.sum(OrderItem.quantity * OrderItem.price).label("revenue")
    ).join(
        OrderItem, Product.id == OrderItem.product_id
    ).join(
        Order, Order.id == OrderItem.order_id
    ).filter(
        Order.status == "completed"
    ).group_by(
        Product.id, Product.name
    ).order_by(
        desc("revenue")
    ).limit(5).all()

    return {
        "total_revenue": db.session.query(func.sum(Order.final_amount)).filter(
            Order.status == "completed").scalar() or 0,
        "total_orders": Order.query.filter_by(status="completed").count(),
        "total_products": Product.query.count(),
        "active_products": Product.query.filter_by(active=True).count(),
        "total_stock": db.session.query(func.sum(Product.stock_quantity)).scalar() or 0,
        "chart_labels": month_keys,
        "chart_revenue": [revenue_map.get(m, {}).get("revenue", 0) for m in month_keys],
        "chart_orders": [revenue_map.get(m, {}).get("orders", 0) for m in month_keys],
        "top_products": top_products,
        "product_labels": [p.name for p in top_products],
        "product_revenue": [float(p.revenue or 0) for p in top_products],
        "product_sold": [int(p.sold_quantity or 0) for p in top_products],
    }


# user admin

def get_user_detail_for_admin(user_id):
    user = User.query.get_or_404(user_id)

    now = datetime.now()
    created_date = user.created_date or now
    account_days = max((now - created_date).days, 0)

    orders = Order.query.filter_by(user_id=user.id) \
        .order_by(Order.created_at.desc()) \
        .all()

    total_orders = len(orders)
    total_spent = sum(float(o.final_amount or 0) for o in orders)
    total_before_discount = sum(float(o.total_amount or 0) for o in orders)
    total_discount = sum(float(o.discount_amount or 0) for o in orders)

    current_coupons = UserCoupon.query.filter_by(
        user_id=user.id,
        is_used=False
    ).order_by(UserCoupon.id.desc()).all()

    used_coupons = UserCoupon.query.filter_by(
        user_id=user.id,
        is_used=True
    ).order_by(UserCoupon.used_at.desc()).all()

    total_items_bought = db.session.query(
        func.coalesce(func.sum(OrderItem.quantity), 0)
    ).join(Order, Order.id == OrderItem.order_id) \
                             .filter(Order.user_id == user.id) \
                             .scalar() or 0

    avg_order_value = total_spent / total_orders if total_orders > 0 else 0

    stats = {
        "account_days": account_days,
        "total_orders": total_orders,
        "total_spent": total_spent,
        "total_before_discount": total_before_discount,
        "total_discount": total_discount,
        "current_coupon_count": len(current_coupons),
        "used_coupon_count": len(used_coupons),
        "total_items_bought": int(total_items_bought),
        "avg_order_value": avg_order_value,
        "last_order": orders[0] if orders else None
    }

    return {
        "user": user,
        "stats": stats,
        "recent_orders": orders[:8],
        "current_coupons": current_coupons,
        "used_coupons": used_coupons[:8]
    }


def admin_create_user_from_form(form):
    name = (form.get("name") or "").strip()
    username = (form.get("username") or "").strip()
    email = (form.get("email") or "").strip().lower()
    phone = (form.get("phone") or "").strip()
    address = (form.get("address") or "").strip()
    password = form.get("password") or ""
    role_raw = form.get("role") or "USER"
    active = str(form.get("active", "")).strip() in ["1", "true", "True", "on"]

    validate_user_form_data_for_admin(
        name=name,
        username=username,
        email=email,
        phone=phone,
        address=address,
        password=password,
        user_id=None,
        require_password=True
    )

    password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()

    user = User(
        name=name,
        username=username,
        email=email,
        phone=phone,
        address=address,
        password=password_hash,
        role=UserRole.ADMIN if role_raw == "ADMIN" else UserRole.USER,
        active=active
    )

    db.session.add(user)
    db.session.commit()

    return user


def toggle_admin_active_status(user_id, current_admin_id=None):
    user = User.query.get_or_404(user_id)

    if user.role != UserRole.ADMIN:
        raise ValueError("Chỉ được thay đổi trạng thái tài khoản admin.")

    if current_admin_id and user.id == current_admin_id:
        raise ValueError("Bạn không thể tự tắt hoạt động tài khoản admin đang đăng nhập.")

    active_admin_count = User.query.filter(
        User.role == UserRole.ADMIN,
        User.active == True
    ).count()

    if user.active and active_admin_count <= 1:
        raise ValueError("Không thể tắt admin cuối cùng đang hoạt động.")

    user.active = not user.active
    db.session.commit()

    return user


def query_users_for_admin(search=None):
    query = User.query

    search = (search or "").strip()
    if search:
        keyword = f"%{search}%"
        query = query.filter(
            (User.name.ilike(keyword)) |
            (User.username.ilike(keyword)) |
            (User.email.ilike(keyword)) |
            (User.phone.ilike(keyword))
        )

    return query.order_by(User.id.desc())


# category admin
def query_categories_for_admin(search=None):
    query = Category.query

    search = (search or "").strip()
    if search:
        keyword = f"%{search}%"
        query = query.filter(Category.name.ilike(keyword))

    return query.order_by(Category.id.desc()).all()


def get_top_categories_by_product_count(limit=3):
    return db.session.query(Category) \
        .join(Product, Product.cate_id == Category.id) \
        .filter(Category.active == True, Product.active == True) \
        .group_by(Category.id) \
        .order_by(func.count(Product.id).desc()) \
        .limit(limit) \
        .all()


def save_category_from_form(category_id, name, description, active):
    name = (name or "").strip()
    description = (description or "").strip()

    if not name:
        raise ValueError("Vui lòng nhập tên danh mục.")

    if category_id:
        category = Category.query.get_or_404(category_id)
        category.name = name
        category.description = description
        category.active = active
    else:
        category = Category(
            name=name,
            description=description,
            active=active
        )
        db.session.add(category)

    db.session.commit()
    return category


def delete_category_by_id(category_id):
    category = Category.query.get_or_404(category_id)

    if category.products:
        category.active = False
        db.session.commit()
        return "soft_delete"

    db.session.delete(category)
    db.session.commit()
    return "hard_delete"


# product admin

# up ảnh
def save_product_images(image_files):
    allowed_exts = {"png", "jpg", "jpeg", "webp"}
    saved_images = []

    for image_file in image_files:
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            ext = filename.rsplit(".", 1)[-1].lower()

            if ext not in allowed_exts:
                raise ValueError("Chỉ được tải lên file ảnh PNG, JPG, JPEG hoặc WEBP.")

            upload_dir = os.path.join(app.root_path, "static", "uploads", "products")
            os.makedirs(upload_dir, exist_ok=True)

            new_filename = f"{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join(upload_dir, new_filename)

            image_file.save(save_path)

            saved_images.append(
                url_for(
                    "static",
                    filename=f"uploads/products/{new_filename}"
                )
            )

    return saved_images


# query
def query_products_for_admin(search=None,
                             category_id=None,
                             price_sort=None,
                             stock_sort=None):
    query = Product.query

    search = (search or "").strip()

    if search:
        keyword = f"%{search}%"
        query = query.filter(Product.name.ilike(keyword))

    if category_id:
        query = query.filter(Product.cate_id == category_id)

    if price_sort == "asc":
        query = query.order_by(Product.price.asc())

    elif price_sort == "desc":
        query = query.order_by(Product.price.desc())

    elif stock_sort == "asc":
        query = query.order_by(Product.stock_quantity.asc())

    elif stock_sort == "desc":
        query = query.order_by(Product.stock_quantity.desc())

    else:
        query = query.order_by(Product.id.desc())

    return query


# create
def create_product_from_form(form, files):
    saved_images = save_product_images(
        files.getlist("image_files")
    )

    description = (form.get("description") or "").strip()
    origin = (form.get("origin") or "").strip()
    warranty = (form.get("warranty") or "").strip()

    if not description:
        raise ValueError("Vui lòng nhập mô tả sản phẩm.")

    if not origin:
        raise ValueError("Vui lòng nhập xuất xứ sản phẩm.")

    if not warranty:
        raise ValueError("Vui lòng nhập thông tin bảo hành.")

    try:
        price = float(form.get("price") or 0)
        stock_quantity = int(form.get("stock_quantity") or 0)
    except ValueError:
        raise ValueError("Giá và số lượng phải là số hợp lệ.")

    if price < 0:
        raise ValueError("Giá sản phẩm không được âm.")

    if stock_quantity < 0:
        raise ValueError("Số lượng sản phẩm không được âm.")

    product = Product(
        name=(form.get("name") or "").strip(),
        price=price,
        stock_quantity=stock_quantity,
        cate_id=int(form.get("cate_id")),
        image=saved_images[0] if saved_images else None,
        active=bool(form.get("active"))
    )

    db.session.add(product)
    db.session.flush()

    for index, img in enumerate(saved_images):
        db.session.add(ProductImage(
            product_id=product.id,
            image=img,
            is_main=(index == 0)
        ))

    detail = ProductDetail(
        product_id=product.id,
        description=description,
        origin=origin,
        warranty=warranty
    )

    db.session.add(detail)

    db.session.commit()

    return product


# edit
def update_product_from_form(product, form, files):
    name = (form.get("name") or "").strip()

    try:
        price = float(form.get("price") or 0)
        stock_quantity = int(form.get("stock_quantity") or 0)
        cate_id = int(form.get("cate_id"))
    except ValueError:
        raise ValueError("Giá, số lượng và danh mục phải hợp lệ.")

    if not name:
        raise ValueError("Vui lòng nhập tên sản phẩm.")

    if price < 0:
        raise ValueError("Giá sản phẩm không được âm.")

    if stock_quantity < 0:
        raise ValueError("Số lượng sản phẩm không được âm.")

    product.name = name
    product.price = price
    product.stock_quantity = stock_quantity
    product.cate_id = cate_id
    product.active = bool(form.get("active"))

    description = (form.get("description") or "").strip()
    origin = (form.get("origin") or "").strip()
    warranty = (form.get("warranty") or "").strip()

    if not description:
        raise ValueError("Vui lòng nhập mô tả sản phẩm.")

    if not origin:
        raise ValueError("Vui lòng nhập xuất xứ sản phẩm.")

    if not warranty:
        raise ValueError("Vui lòng nhập thông tin bảo hành.")

    detail = product.product_detail

    if not detail:
        detail = ProductDetail(product_id=product.id)
        db.session.add(detail)

    detail.description = description
    detail.origin = origin
    detail.warranty = warranty

    remove_ids = form.getlist("remove_image_ids")

    if remove_ids:
        ProductImage.query.filter(
            ProductImage.product_id == product.id,
            ProductImage.id.in_(remove_ids)
        ).delete(synchronize_session=False)

    saved_images = save_product_images(
        files.getlist("image_files")
    )

    for img in saved_images:
        db.session.add(ProductImage(
            product_id=product.id,
            image=img,
            is_main=False
        ))

    db.session.flush()

    images = ProductImage.query.filter_by(
        product_id=product.id
    ).order_by(ProductImage.id.asc()).all()

    for index, img in enumerate(images):
        img.is_main = (index == 0)

    product.image = images[0].image if images else None

    db.session.commit()

    return product


# delete
def delete_product_by_id(product_id):
    product = Product.query.get_or_404(product_id)

    has_order = OrderItem.query.filter_by(product_id=product.id).first()
    has_cart = CartItem.query.filter_by(product_id=product.id).first()

    if has_order or has_cart:
        product.active = False
        db.session.commit()
        return "soft_delete"

    CouponProduct.query.filter_by(
        product_id=product.id
    ).delete(synchronize_session=False)

    ProductImage.query.filter_by(
        product_id=product.id
    ).delete(synchronize_session=False)

    ProductDetail.query.filter_by(
        product_id=product.id
    ).delete(synchronize_session=False)

    db.session.delete(product)

    db.session.commit()

    return "hard_delete"


def paginate_list(items, page=1, page_size=None):
    page = int(page or 1)

    if page < 1:
        page = 1

    page_size = page_size or app.config["PAGE_SIZE"]

    total = len(items)
    pages = math.ceil(total / page_size) if total > 0 else 1

    if page > pages:
        page = pages

    start = (page - 1) * page_size
    end = start + page_size

    return {
        "items": items[start:end],
        "page": page,
        "pages": pages,
        "total": total,
        "page_size": page_size,
        "has_next": page < pages,
        "has_prev": page > 1
    }


# Chi tiet don hang admin

def get_recent_order_notifications(limit=5):
    return Order.query.order_by(Order.created_at.desc()).limit(limit).all()


def count_new_orders():
    return Order.query.filter_by(status="placed").count()


def query_orders_for_admin(search=None):
    query = Order.query.join(User, Order.user_id == User.id)

    search = (search or "").strip()
    if search:
        keyword = f"%{search}%"
        query = query.filter(
            (User.name.ilike(keyword)) |
            (User.username.ilike(keyword)) |
            (Order.id == search if search.isdigit() else False)
        )

    return query.order_by(Order.created_at.desc())


def get_order_detail_for_admin(order_id):
    return Order.query.get_or_404(order_id)
