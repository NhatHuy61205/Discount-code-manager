import random
from datetime import datetime, timedelta

from app import app, db
from app.models import *

def seed_data():
    # ===== 1. CATEGORY =====
    categories = [
        Category(name="Áo", description="Quần áo thời trang"),
        Category(name="Giày", description="Giày sneaker, thể thao"),
        Category(name="Phụ kiện", description="Túi, đồng hồ, balo"),
    ]
    db.session.add_all(categories)
    db.session.commit()

    # ===== 2. USERS =====
    users = []
    for i in range(5):
        u = User(
            name=f"User {i}",
            username=f"user{i}",
            password="123456",
            email=f"user{i}@gmail.com",
            phone="0900000000",
            address="HCM",
            role=UserRole.USER
        )
        users.append(u)

    admin = User(
        name="Admin",
        username="admin",
        password="admin123",
        email="admin@gmail.com",
        phone="0999999999",
        address="HCM",
        role=UserRole.ADMIN
    )

    db.session.add_all(users + [admin])
    db.session.commit()

    # ===== 3. PRODUCTS =====
    products = []
    for i in range(10):
        p = Product(
            name=f"Sản phẩm {i}",
            price=random.randint(100, 500) * 1000,
            cate_id=random.choice(categories).id,
            image="https://via.placeholder.com/300"
        )
        products.append(p)

    db.session.add_all(products)
    db.session.commit()

    # ===== 4. PRODUCT DETAIL =====
    for p in products:
        detail = ProductDetail(
            product_id=p.id,
            description="Mô tả sản phẩm",
            origin="Việt Nam",
            warranty="12 tháng"
        )
        db.session.add(detail)

    db.session.commit()

    # ===== 5. COUPON TYPE =====
    coupon_types = [
        CouponType(name="Giảm toàn shop", description="Áp dụng toàn bộ"),
        CouponType(name="Giảm theo danh mục", description="Áp dụng theo category"),
    ]
    db.session.add_all(coupon_types)
    db.session.commit()

    # ===== 6. COUPONS =====
    coupons = []
    for i in range(5):
        c = Coupon(
            name=f"Coupon {i}",
            code=f"SALE{i}",
            discount_kind=DiscountKind.PERCENTAGE,
            discount_value=random.choice([10, 20, 30]),
            quantity=100,
            end_date=datetime.now() + timedelta(days=30),
            coupon_type_id=random.choice(coupon_types).id
        )
        coupons.append(c)

    db.session.add_all(coupons)
    db.session.commit()

    # ===== 7. USER COUPON =====
    for u in users:
        uc = UserCoupon(
            user_id=u.id,
            coupon_id=random.choice(coupons).id
        )
        db.session.add(uc)

    db.session.commit()

    # ===== 8. CART =====
    carts = []
    for u in users:
        cart = Cart(
            user_id=u.id,
            coupon_id=random.choice(coupons).id
        )
        carts.append(cart)

    db.session.add_all(carts)
    db.session.commit()

    # ===== 9. CART ITEM =====
    for cart in carts:
        for _ in range(2):
            item = CartItem(
                cart_id=cart.id,
                product_id=random.choice(products).id,
                quantity=random.randint(1, 3),
                price=random.randint(100, 500) * 1000
            )
            db.session.add(item)

    db.session.commit()

    # ===== 10. ORDERS =====
    orders = []
    for u in users:
        o = Order(
            user_id=u.id,
            coupon_id=random.choice(coupons).id,
            total_amount=500000,
            discount_amount=50000,
            final_amount=450000,
            status="completed"
        )
        orders.append(o)

    db.session.add_all(orders)
    db.session.commit()

    # ===== 11. ORDER ITEMS =====
    for o in orders:
        for _ in range(2):
            oi = OrderItem(
                order_id=o.id,
                product_id=random.choice(products).id,
                quantity=random.randint(1, 3),
                price=random.randint(100, 500) * 1000
            )
            db.session.add(oi)

    db.session.commit()

    print("✅ Seed data thành công!")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # tạo bảng nếu chưa có
        seed_data()