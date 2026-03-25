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
            image="https://via.placeholder.com/300",
            stock_quantity=random.randint(0, 200)
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
        CouponType(name="Giảm toàn bộ sản phẩm", description="Áp dụng toàn shop"),
        CouponType(name="Giảm theo ngành hàng", description="Áp dụng theo loại sản phẩm"),
        CouponType(name="Giảm theo sản phẩm", description="Áp dụng theo sản phẩm được chọn"),
    ]
    db.session.add_all(coupon_types)
    db.session.commit()

    # ===== 6. COUPONS =====
    coupons = []

    for i in range(5):
        c = Coupon(
            name=f"Giảm giá {i}",
            code=f"SALE{i}",
            description="Đơn từ 50.000đ - Áp dụng toàn shop",

            discount_kind=random.choice([
                DiscountKind.PERCENTAGE,
                DiscountKind.FIXED
            ]),

            discount_value=random.choice([10, 20, 30, 50000, 100000]),

            apply_type=random.choice([
                CouponApplyType.ALL_PRODUCT,
                CouponApplyType.CATEGORY,
                CouponApplyType.PRODUCT
            ]),

            target_type=random.choice([
                CouponTargetType.ALL,
                CouponTargetType.LOYAL_1Y
            ]),

            status=CouponStatus.ACTIVE,

            min_order_value=50000,
            max_discount_value=100000,

            quantity=100,
            used_count=random.randint(0, 50),

            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=30),

            show_public=random.choice([True, False]),
            usage_limit_per_user=random.choice([1, 999999]),

            coupon_type_id=random.choice(coupon_types).id
        )
        coupons.append(c)

    # Coupon hết hạn
    coupons.append(Coupon(
        name="Hết hạn",
        code="EXPIRED1",
        description="Coupon đã hết hạn",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=20,
        apply_type=CouponApplyType.ALL_PRODUCT,
        show_public=True,
        usage_limit_per_user=1,
        target_type=CouponTargetType.ALL,
        status=CouponStatus.ACTIVE,
        quantity=100,
        used_count=10,
        start_date=datetime.now() - timedelta(days=10),
        end_date=datetime.now() - timedelta(days=1),
    ))

    # Coupon hết lượt
    coupons.append(Coupon(
        name="Hết lượt",
        code="OUT1",
        description="Đã hết lượt sử dụng",
        discount_kind=DiscountKind.FIXED,
        discount_value=50000,
        apply_type=CouponApplyType.ALL_PRODUCT,
        show_public=False,
        usage_limit_per_user=999999,
        target_type=CouponTargetType.ALL,
        status=CouponStatus.ACTIVE,
        quantity=50,
        used_count=50,
        start_date=datetime.now() - timedelta(days=5),
        end_date=datetime.now() + timedelta(days=10),
    ))

    # Coupon sắp diễn ra
    coupons.append(Coupon(
        name="Sắp diễn ra",
        code="COMING1",
        description="Chưa tới ngày bắt đầu",
        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=15,
        apply_type=CouponApplyType.ALL_PRODUCT,
        show_public=True,
        usage_limit_per_user=1,
        target_type=CouponTargetType.ALL,
        status=CouponStatus.ACTIVE,
        quantity=100,
        used_count=0,
        start_date=datetime.now() + timedelta(days=2),
        end_date=datetime.now() + timedelta(days=10),
    ))

    db.session.add_all(coupons)
    db.session.commit()
    # ===== 6.1 COUPON CATEGORY =====
    for c in coupons:
        if c.apply_type == CouponApplyType.CATEGORY:
            selected_categories = random.sample(categories, k=random.randint(1, min(2, len(categories))))
            for cate in selected_categories:
                db.session.add(CouponCategory(
                    coupon_id=c.id,
                    category_id=cate.id
                ))

    db.session.commit()

    # ===== 6.2 COUPON PRODUCT =====
    for c in coupons:
        if c.apply_type == CouponApplyType.PRODUCT:
            selected_products = random.sample(products, k=random.randint(1, min(4, len(products))))
            for p in selected_products:
                db.session.add(CouponProduct(
                    coupon_id=c.id,
                    product_id=p.id
                ))

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
        db.drop_all()
        db.create_all()
        seed_data()