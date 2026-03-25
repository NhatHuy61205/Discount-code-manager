import hashlib
from datetime import datetime

from app import app, db
from app import login
from app.models import User, CouponStatus, CouponCondition


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

def get_remaining_quantity(coupon):
    """
    Số lượng còn lại = tổng - đã dùng
    """
    return max((coupon.quantity or 0) - (coupon.used_count or 0), 0)


def get_usage_text(coupon):
    """
    Hiển thị dạng: 0/100
    """
    return f"{coupon.used_count or 0}/{coupon.quantity or 0}"


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


    if coupon.quantity is not None and (coupon.used_count or 0) >= (coupon.quantity or 0):
        return CouponCondition.OUT_OF_STOCK

    return CouponCondition.AVAILABLE