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
            phone=f"090000000{i}",
            address="TP.HCM",
            role=UserRole.USER
        )
        users.append(u)

    admin = User(
        name="Admin",
        username="admin",
        password="admin123",
        email="admin@gmail.com",
        phone="0999999999",
        address="TP.HCM",
        role=UserRole.ADMIN
    )

    db.session.add_all(users + [admin])
    db.session.commit()

    # ===== 2.1 ADDRESS =====
    sample_addresses = [
        "A56 Nguyễn Trãi, Quận 1, TP.HCM",
        "123 Lê Lợi, Quận 3, TP.HCM",
        "45 Điện Biên Phủ, Bình Thạnh, TP.HCM",
        "78 Võ Văn Tần, Quận 3, TP.HCM",
        "12 Nguyễn Huệ, Quận 1, TP.HCM",
        "25 Cách Mạng Tháng 8, Quận 10, TP.HCM",
        "90 Phan Xích Long, Phú Nhuận, TP.HCM",
    ]

    for u in users:
        used_address_lines = random.sample(sample_addresses, 2)

        for j, address_line in enumerate(used_address_lines):
            addr = Address(
                name=f"Địa chỉ {j + 1} - {u.name}",
                recipient_name=u.name,
                phone=u.phone,
                address_line=address_line
            )
            db.session.add(addr)
            db.session.flush()

            ua = UserAddress(
                user_id=u.id,
                address_id=addr.id,
                is_default=(j == 0)
            )
            db.session.add(ua)

    admin_addr = Address(
        name="Địa chỉ admin",
        recipient_name=admin.name,
        phone=admin.phone,
        address_line="1 Nguyễn Huệ, Quận 1, TP.HCM"
    )
    db.session.add(admin_addr)
    db.session.flush()

    db.session.add(UserAddress(
        user_id=admin.id,
        address_id=admin_addr.id,
        is_default=True
    ))

    db.session.commit()

    # ===== 3. PRODUCTS =====
    products = []
    for i in range(10):
        p = Product(
            name=f"Sản phẩm {i}",
            price=random.randint(100, 500) * 1000,
            cate_id=random.choice(categories).id,
            stock_quantity=random.randint(1, 200)
        )
        products.append(p)

    db.session.add_all(products)
    db.session.commit()

    # ===== 4. PRODUCT DETAIL =====
    for p in products:
        num_images = random.randint(2, 4)

        for idx in range(num_images):
            img_url = f"https://via.placeholder.com/300?text={p.name}-{idx}"

            img = ProductImage(
                product_id=p.id,
                image=img_url,
                is_main=(idx == 0)
            )
            db.session.add(img)

            if idx == 0:
                p.image = img_url
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
        discount_kind = random.choice([
            DiscountKind.PERCENTAGE,
            DiscountKind.FIXED
        ])

        discount_value = random.choice([10, 15, 20, 30000, 50000])

        max_discount_value = 100000 if discount_kind == DiscountKind.PERCENTAGE else None

        c = Coupon(
            name=f"Giảm giá {i}",
            code=f"SALE{i}",
            description="Đơn từ 50.000đ - Áp dụng toàn shop",
            discount_kind=discount_kind,
            discount_value=discount_value,
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
            max_discount_value=max_discount_value,
            quantity=100,
            used_count=random.randint(0, 20),
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=30),
            show_public=random.choice([True, False]),
            usage_limit_per_user=random.choice([1, 999999]),
            coupon_type_id=random.choice(coupon_types).id
        )
        coupons.append(c)

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
        max_discount_value=50000
    ))

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
        max_discount_value=50000
    ))

    db.session.add_all(coupons)
    db.session.commit()

    # ===== 6.1 COUPON CATEGORY =====
    for c in coupons:
        if c.apply_type == CouponApplyType.CATEGORY:
            selected_categories = random.sample(
                categories,
                k=random.randint(1, min(2, len(categories)))
            )
            for cate in selected_categories:
                db.session.add(CouponCategory(
                    coupon_id=c.id,
                    category_id=cate.id
                ))

    db.session.commit()

    # ===== 6.2 COUPON PRODUCT =====
    for c in coupons:
        if c.apply_type == CouponApplyType.PRODUCT:
            selected_products = random.sample(
                products,
                k=random.randint(1, min(4, len(products)))
            )
            for p in selected_products:
                db.session.add(CouponProduct(
                    coupon_id=c.id,
                    product_id=p.id
                ))

    db.session.commit()

    # ===== 7. USER COUPON =====
    for u in users:
        owned_coupons = random.sample(coupons, k=2)
        for idx, coupon in enumerate(owned_coupons):
            db.session.add(UserCoupon(
                user_id=u.id,
                coupon_id=coupon.id,
                is_used=(idx == 1),
                used_at=datetime.now() - timedelta(days=1) if idx == 1 else None
            ))

    db.session.commit()

    # ===== 8. CART =====
    carts = []
    usable_coupon_ids = [c.id for c in coupons if c.end_date and c.end_date >= datetime.now()]

    for u in users:
        cart = Cart(
            user_id=u.id,
            coupon_id=random.choice(usable_coupon_ids) if usable_coupon_ids else None
        )
        carts.append(cart)

    db.session.add_all(carts)
    db.session.commit()

    # ===== 9. CART ITEM =====
    for cart in carts:
        selected_products = random.sample(products, k=2)
        for product in selected_products:
            item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=random.randint(1, 3),
                price=product.price
            )
            db.session.add(item)

    db.session.commit()

    # ===== 10. ORDERS =====
    orders = []
    for u in users:
        total_amount = random.randint(300000, 800000)
        discount_amount = random.randint(10000, 50000)

        if discount_amount >= total_amount:
            discount_amount = int(total_amount * 0.1)

        final_amount = total_amount - discount_amount

        selected_coupon = random.choice(coupons) if coupons else None

        o = Order(
            user_id=u.id,
            coupon_id=selected_coupon.id if selected_coupon else None,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            status=OrderStatus.COMPLETED
        )
        orders.append(o)

    db.session.add_all(orders)
    db.session.commit()

    # ===== 11. ORDER ITEMS =====
    sample_notes = [
        None,
        "Gọi trước khi giao",
        "Đóng gói cẩn thận",
        "Kiểm tra hàng trước khi gửi",
        "Không gọi giờ nghỉ trưa",
        "Giao giờ hành chính"
    ]

    for o in orders:
        selected_products = random.sample(products, k=min(2, len(products)))

        for product in selected_products:
            quantity = random.randint(1, 3)
            note = random.choice(sample_notes)

            oi = OrderItem(
                order_id=o.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price,
                note=note
            )
            db.session.add(oi)

    db.session.commit()

    print("✅ Seed data thành công!")


if __name__ == "__main__":
    with app.app_context():
        seed_data()
