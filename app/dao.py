import hashlib
import re
from datetime import datetime

from app import app, db
from app import login
from app.models import User, CouponStatus, CouponCondition, Product, CouponApplyType, DiscountKind, Coupon, Category, \
    CouponCategory, CouponProduct, CouponTargetType, Cart, UserCoupon


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


def register_user(name, username, email, phone, address, password, confirm):
    name = (name or "").strip()
    username = (username or "").strip()
    email = (email or "").strip()
    phone = (phone or "").strip()
    address = (address or "").strip()
    password = password or ""
    confirm = confirm or ""

    if not all([name, username, email, address, password, confirm]):
        raise ValueError("Vui lòng nhập đầy đủ thông tin")

    if len(password) < 8:
        raise ValueError("Mật khẩu phải tối thiểu 8 ký tự")

    if not re.search(r"[A-Za-z]", password):
        raise ValueError("Mật khẩu phải chứa chữ")

    if not re.search(r"\d", password):
        raise ValueError("Mật khẩu phải chứa số")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Mật khẩu phải chứa ký tự đặc biệt")

    if password != confirm:
        raise ValueError("Mật khẩu không khớp")

    if phone and not re.fullmatch(r"\d{10}", phone):
        raise ValueError("Số điện thoại phải đúng 10 chữ số")

    if get_user_by_username(username):
        raise ValueError("Tên đăng nhập đã tồn tại")

    if get_user_by_email(email):
        raise ValueError("Email đã tồn tại")

    if phone and get_user_by_phone(phone):
        raise ValueError("Số điện thoại đã được sử dụng")

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
    if coupon.discount_kind == DiscountKind.PERCENTAGE:
        discount = product.price * (coupon.discount_value / 100)
        if coupon.max_discount_value:
            discount = min(discount, coupon.max_discount_value)
        return discount

    return coupon.discount_value


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
    now = datetime.now()

    user_coupons = UserCoupon.query.filter_by(user_id=user.id) \
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
    cart = user.carts
    return cart.cart_items if cart else []


# PRODUCT

def get_active_products():
    return Product.query.filter_by(active=True).all()


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
    return categories, products


# Tạo mã giảm giá
def create_coupon_from_form(form):
    name = form.get("name", "").strip()
    code = form.get("code", "").strip().upper()
    description = form.get("description", "").strip()

    discount_kind_raw = form.get("discount_kind", "fixed")
    apply_scope = form.get("apply_scope", "all_product")
    target_type_raw = form.get("target_type", "all")

    max_discount_value = form.get("max_discount_value")
    max_discount_value = float(max_discount_value) if max_discount_value else None

    discount_value = float(form.get("discount_value") or 0)
    min_order_value = float(form.get("min_order_value") or 0)
    quantity = int(form.get("quantity") or 0)

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
    name = form_data["name"]
    code = form_data["code"]
    description = form_data["description"]

    discount_kind_raw = form_data["discount_kind"]
    discount_value = float(form_data["discount_value"] or 0)
    min_order_value = float(form_data["min_order_value"] or 0)
    quantity = int(form_data["quantity"] or 0)
    show_public = str(form_data.get("show_public", "")).strip() in ["1", "true", "True", "on"]
    max_discount_value_raw = form_data["max_discount_value"]
    max_discount_value = float(max_discount_value_raw) if str(max_discount_value_raw).strip() != "" else None

    submitted_start_date = parse_datetime_local(form_data["start_date"])
    end_date = parse_datetime_local(form_data["end_date"])
    status_raw = form_data["status"]
    now = datetime.now()

    original_start_date = coupon.start_date
    can_edit_start_date = original_start_date and original_start_date > now

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

    if quantity <= 0:
        raise ValueError("Số lượng không hợp lệ.")

    if min_order_value < 0:
        raise ValueError("Giá trị đơn tối thiểu không hợp lệ.")

    if can_edit_start_date:
        if not start_date:
            raise ValueError("Vui lòng nhập ngày bắt đầu.")
        if start_date < now:
            raise ValueError("Thời gian bắt đầu phải lớn hơn hoặc bằng thời điểm hiện tại.")
    else:
        original_start_date_str = original_start_date.strftime("%d/%m/%Y %H:%M") if original_start_date else ""
        submitted_start_date_str = (form_data.get("start_date") or "").strip()

        if submitted_start_date_str != original_start_date_str:
            raise ValueError("Mã giảm giá đã tới ngày bắt đầu, không được chỉnh sửa ngày bắt đầu nữa.")

    if not end_date:
        raise ValueError("Vui lòng nhập ngày kết thúc.")

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
    db.session.delete(coupon)
    db.session.commit()
    return coupon
