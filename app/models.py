from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Float, ForeignKey, Text, UniqueConstraint, \
    Table
from datetime import datetime
from sqlalchemy.orm import relationship
from app import app, db, login
from enum import Enum as RoleEnum
from flask_login import UserMixin


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.now)
    active = Column(Boolean, default=True)

    def __str__(self):
        return self.name


class UserRole(RoleEnum):
    USER = 1
    ADMIN = 2


class User(Base, UserMixin):
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(db.String(20))
    role = Column(Enum(UserRole), default=UserRole.USER)
    address = Column(db.String(255), nullable=False)

    orders = relationship('Order', backref="user", lazy=True)
    carts = relationship('Cart', backref='user', uselist=False)
    user_coupons = relationship('UserCoupon', backref='user', lazy=True)
    user_addresses = relationship('UserAddress', backref='user', lazy=True)


class Address(Base):
    recipient_name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)
    address_line = Column(String(255), nullable=False)

    user_addresses = relationship('UserAddress', backref='address', lazy=True)

    def __str__(self):
        return self.address_line


class UserAddress(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    address_id = Column(Integer, ForeignKey(Address.id), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'address_id', name='uq_user_address'),
    )


class Category(Base):
    description = Column(Text)

    products = relationship('Product', backref="category", lazy=True)
    coupon_categories = relationship('CouponCategory', backref='category', lazy=True)


class Product(Base):
    image = Column(String(300), nullable=True)
    price = Column(Float, default=0.0)
    cate_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)

    product_detail = relationship('ProductDetail', backref='product', uselist=False)
    order_items = relationship('OrderItem', backref='product', lazy=True)
    coupon_products = relationship('CouponProduct', backref='product', lazy=True)


class Cart(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, db.ForeignKey(User.id), unique=True)
    coupon_id = Column(Integer, ForeignKey('coupon.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    cart_items = relationship('CartItem', backref='cart', lazy=True)


class CartItem(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey(Cart.id))
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float)

    product = relationship('Product', backref='cart_items')


class ProductDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id), unique=True)
    description = db.Column(db.Text)
    origin = db.Column(db.String(100))
    warranty = db.Column(db.String(100))


class DiscountKind(RoleEnum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class CouponApplyType(RoleEnum):
    ALL_PRODUCT = "all_product"  # Áp dụng toàn bộ sản phẩm
    CATEGORY = "category"  # Áp dụng theo loại sản phẩm
    PRODUCT = "product"  # Áp dụng theo sản phẩm được chọn


class CouponTargetType(RoleEnum):
    ALL = "all"  # Tất cả mọi người
    LOYAL_1Y = "loyal_1y"  # User có tài khoản trên 1 năm


class CouponStatus(RoleEnum):
    DRAFT = "draft"  # Bản nháp
    ACTIVE = "active"  # Đang bật
    INACTIVE = "inactive"  # Tắt thủ công


class CouponCondition(RoleEnum):
    UPCOMING = "upcoming"  # Chưa tới ngày bắt đầu
    AVAILABLE = "available"  # Đang dùng được
    OUT_OF_STOCK = "out_of_stock"  # Hết lượt
    EXPIRED = "expired"  # Hết hạn
    DISABLED = "disabled"  # Bị tắt


class CouponType(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(Text)

    coupons = relationship('Coupon', backref='coupon_type', lazy=True)


class Coupon(Base):
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    discount_kind = Column(Enum(DiscountKind), nullable=False)
    discount_value = Column(Float, nullable=False)

    apply_type = Column(Enum(CouponApplyType), default=CouponApplyType.ALL_PRODUCT, nullable=False)
    target_type = Column(Enum(CouponTargetType), default=CouponTargetType.ALL, nullable=False)
    status = Column(Enum(CouponStatus), default=CouponStatus.DRAFT, nullable=False)

    min_order_value = Column(Float, default=0)
    max_discount_value = Column(Float, nullable=True)

    quantity = Column(Integer, default=0)
    used_count = Column(Integer, default=0)

    start_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime)

    show_public = Column(Boolean, default=False)
    usage_limit_per_user = Column(Integer, default=1)

    coupon_type_id = Column(Integer, ForeignKey(CouponType.id), nullable=True)

    user_coupons = relationship('UserCoupon', backref='coupon', lazy=True)
    carts = relationship('Cart', backref='coupon', lazy=True)
    orders = relationship('Order', backref='coupon', lazy=True)
    coupon_categories = relationship('CouponCategory', backref='coupon', lazy=True)
    coupon_products = relationship('CouponProduct', backref='coupon', lazy=True)


class CouponCategory(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey(Coupon.id), nullable=False)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)

    __table_args__ = (
        UniqueConstraint('coupon_id', 'category_id', name='uq_coupon_category'),
    )


class CouponProduct(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey(Coupon.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)

    __table_args__ = (
        UniqueConstraint('coupon_id', 'product_id', name='uq_coupon_product'),
    )


class UserCoupon(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    coupon_id = Column(Integer, ForeignKey(Coupon.id), nullable=False)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'coupon_id', name='uq_user_coupon'),
    )


class OrderStatus(RoleEnum):
    PLACED = "placed"
    PROCESSING = "processing"
    SHIPPING = "shipping"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(db.Model):
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey(User.id))
    coupon_id = Column(Integer, ForeignKey(Coupon.id))

    total_amount = Column(Float)
    discount_amount = Column(Float)
    final_amount = Column(Float)

    status = Column(Enum(OrderStatus), default=OrderStatus.PLACED)
    created_at = Column(DateTime, default=datetime.now)

    order_items = relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey(Order.id))
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    quantity = Column(Integer)
    price = Column(Float)
    note = Column(Text, nullable=True)


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
