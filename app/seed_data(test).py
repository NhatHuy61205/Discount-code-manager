import random
from datetime import datetime, timedelta

from app import app, db
from app.models import *


def seed_data():
    # ===== RESET DATABASE =====
    db.drop_all()
    db.create_all()

    # =========================================================
    # 1. CATEGORY
    # =========================================================
    categories = [
        Category(name="Áo", description="Quần áo thời trang"),
        Category(name="Giày", description="Giày sneaker, thể thao"),
        Category(name="Phụ kiện", description="Túi, balo, đồng hồ"),
    ]

    db.session.add_all(categories)
    db.session.commit()

    cate_map = {c.name: c for c in categories}

    # =========================================================
    # 2. USERS
    # =========================================================
    users = []

    for i in range(1, 6):
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

    # =========================================================
    # 3. ADDRESS
    # =========================================================
    sample_addresses = [
        "12 Nguyễn Huệ, Quận 1",
        "45 Điện Biên Phủ, Bình Thạnh",
        "90 Phan Xích Long, Phú Nhuận",
        "25 CMT8, Quận 10",
        "78 Võ Văn Tần, Quận 3",
    ]

    for u in users:
        for j in range(2):
            addr = Address(
                name=f"Địa chỉ {j + 1}",
                recipient_name=u.name,
                phone=u.phone,
                address_line=random.choice(sample_addresses)
            )

            db.session.add(addr)
            db.session.flush()

            db.session.add(UserAddress(
                user_id=u.id,
                address_id=addr.id,
                is_default=(j == 0)
            ))

    db.session.commit()

    # =========================================================
    # 4. PRODUCTS
    # =========================================================
    # Quy tắc:
    # - Áo -> tên bắt đầu bằng "Áo"
    # - Giày -> tên bắt đầu bằng "Giày"
    # - Phụ kiện -> tên bắt đầu bằng "Phụ kiện"

    product_data = {
        "Áo": [
            "Áo Hoodie Basic",
            "Áo Thun Local Brand",
            "Áo Polo Premium",
            "Áo Sweater Form Rộng",
            "Áo Khoác Denim",
            "Áo Sơ Mi Trắng",
            "Áo Cardigan Hàn Quốc",
        ],

        "Giày": [
            "Giày Sneaker Trắng",
            "Giày Running Sport",
            "Giày Jordan High",
            "Giày Vans Classic",
            "Giày Trainer Pro",
            "Giày Thể Thao Đen",
            "Giày Da Công Sở",
        ],

        "Phụ kiện": [
            "Phụ kiện Balo Basic",
            "Phụ kiện Túi Đeo Chéo",
            "Phụ kiện Nón Lưỡi Trai",
            "Phụ kiện Đồng Hồ Classic",
            "Phụ kiện Ví Da Mini",
            "Phụ kiện Kính Mát",
        ]
    }

    products = []

    for cate_name, names in product_data.items():
        cate = cate_map[cate_name]

        for name in names:
            p = Product(
                name=name,
                price=random.randint(150, 700) * 1000,
                cate_id=cate.id,
                stock_quantity=random.randint(10, 200)
            )

            products.append(p)

    db.session.add_all(products)
    db.session.commit()


    # =========================================================
    # 5. PRODUCT IMAGE
    # =========================================================
    category_images = {
        "Giày": [
            "/static/pics/pics_product3.jpg",  # ảnh chính giày
            "/static/pics/pics_product2.jpg",
            "/static/pics/pics_product1.jpg",
        ],
        "Áo": [
            "/static/pics/pics_product2.jpg",
            "/static/pics/pics_product3.jpg",
            "/static/pics/pics_product1.jpg",
        ],
        "Phụ kiện": [
            "/static/pics/pics_product1.jpg",
            "/static/pics/pics_product3.jpg",
            "/static/pics/pics_product2.jpg",
        ]
    }

    for p in products:
        image_list = category_images.get(p.category.name, [])

        for idx, img_url in enumerate(image_list):
            db.session.add(ProductImage(
                product_id=p.id,
                image=img_url,
                is_main=(idx == 0)
            ))

            if idx == 0:
                p.image = img_url

    db.session.commit()

    # =========================================================
    # 6. COUPON TYPE
    # =========================================================
    coupon_types = [
        CouponType(
            name="Giảm toàn shop",
            description="Áp dụng toàn bộ sản phẩm"
        ),

        CouponType(
            name="Giảm theo ngành hàng",
            description="Áp dụng theo danh mục"
        ),

        CouponType(
            name="Giảm theo sản phẩm",
            description="Áp dụng theo sản phẩm cụ thể"
        ),
    ]

    db.session.add_all(coupon_types)
    db.session.commit()

    # =========================================================
    # 7. COUPONS
    # =========================================================
    # Tạo:
    # - 7 mã toàn bộ
    # - 7 mã ngành hàng
    # - 6 mã sản phẩm
    # Tổng cộng = 20 mã

    coupons = []

    # ---------------------------------------------------------
    # 7.1 MÃ GIẢM TOÀN BỘ
    # ---------------------------------------------------------
    for i in range(1, 8):
        c = Coupon(
            name=f"Giảm toàn shop {i}",
            code=f"ALL{i}",

            description="Giảm giá toàn bộ sản phẩm",

            discount_kind=random.choice([
                DiscountKind.PERCENTAGE,
                DiscountKind.FIXED
            ]),

            discount_value=random.choice([
                10, 15, 20,
                30000, 50000
            ]),

            apply_type=CouponApplyType.ALL_PRODUCT,
            target_type=CouponTargetType.ALL,

            status=CouponStatus.ACTIVE,

            min_order_value=random.choice([
                100000,
                200000,
                300000
            ]),

            max_discount_value=100000,

            quantity=100,
            used_count=random.randint(0, 20),

            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=30),

            show_public=True,
            usage_limit_per_user=random.choice([1, 2]),

            coupon_type_id=coupon_types[0].id
        )

        coupons.append(c)

    # ---------------------------------------------------------
    # 7.2 MÃ GIẢM THEO NGÀNH HÀNG
    # ---------------------------------------------------------
    category_coupons = []

    for i in range(1, 8):
        c = Coupon(
            name=f"Giảm ngành hàng {i}",
            code=f"CATE{i}",

            description="Giảm theo ngành hàng",

            discount_kind=random.choice([
                DiscountKind.PERCENTAGE,
                DiscountKind.FIXED
            ]),

            discount_value=random.choice([
                10, 15, 20,
                30000, 50000
            ]),

            apply_type=CouponApplyType.CATEGORY,
            target_type=CouponTargetType.ALL,

            status=CouponStatus.ACTIVE,

            min_order_value=random.choice([
                100000,
                200000,
                300000
            ]),

            max_discount_value=100000,

            quantity=50,
            used_count=random.randint(0, 10),

            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=20),

            show_public=True,
            usage_limit_per_user=1,

            coupon_type_id=coupon_types[1].id
        )

        coupons.append(c)
        category_coupons.append(c)

    # ---------------------------------------------------------
    # 7.3 MÃ GIẢM THEO SẢN PHẨM
    # ---------------------------------------------------------
    product_coupons = []

    for i in range(1, 7):
        c = Coupon(
            name=f"Giảm sản phẩm {i}",
            code=f"PRO{i}",

            description="Giảm theo sản phẩm cụ thể",

            discount_kind=random.choice([
                DiscountKind.PERCENTAGE,
                DiscountKind.FIXED
            ]),

            discount_value=random.choice([
                10, 15, 20,
                30000, 50000
            ]),

            apply_type=CouponApplyType.PRODUCT,
            target_type=CouponTargetType.ALL,

            status=CouponStatus.ACTIVE,

            min_order_value=random.choice([
                100000,
                200000,
                300000
            ]),

            max_discount_value=100000,

            quantity=30,
            used_count=random.randint(0, 5),

            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=15),

            show_public=True,
            usage_limit_per_user=1,

            coupon_type_id=coupon_types[2].id
        )

        coupons.append(c)
        product_coupons.append(c)

    db.session.add_all(coupons)
    db.session.commit()

    # ---------------------------------------------------------
    # 7.4 MÃ HẾT HẠN
    # ---------------------------------------------------------
    expired_coupon = Coupon(
        name="Mã hết hạn",
        code="EXPIRED",

        description="Coupon đã hết hạn",

        discount_kind=DiscountKind.PERCENTAGE,
        discount_value=15,

        apply_type=CouponApplyType.ALL_PRODUCT,
        target_type=CouponTargetType.ALL,

        status=CouponStatus.ACTIVE,

        min_order_value=100000,
        max_discount_value=50000,

        quantity=100,
        used_count=50,

        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now() - timedelta(days=1),

        show_public=True,
        usage_limit_per_user=1,

        coupon_type_id=coupon_types[0].id
    )

    coupons.append(expired_coupon)

    # ---------------------------------------------------------
    # 7.5 MÃ HẾT LƯỢT
    # ---------------------------------------------------------
    out_coupon = Coupon(
        name="Mã hết lượt",
        code="OUT100",

        description="Đã hết số lượng sử dụng",

        discount_kind=DiscountKind.FIXED,
        discount_value=100000,

        apply_type=CouponApplyType.ALL_PRODUCT,
        target_type=CouponTargetType.ALL,

        status=CouponStatus.ACTIVE,

        min_order_value=500000,

        quantity=20,
        used_count=20,

        start_date=datetime.now() - timedelta(days=2),
        end_date=datetime.now() + timedelta(days=10),

        show_public=True,
        usage_limit_per_user=1,

        coupon_type_id=coupon_types[0].id
    )

    coupons.append(out_coupon)

    db.session.add_all(coupons)
    db.session.commit()

    # =========================================================
    # 8. COUPON CATEGORY
    # =========================================================
    for c in category_coupons:
        selected_categories = random.sample(
            categories,
            k=random.randint(1, 2)
        )

        for cate in selected_categories:
            db.session.add(
                CouponCategory(
                    coupon_id=c.id,
                    category_id=cate.id
                )
            )

    db.session.commit()

    # =========================================================
    # 9. COUPON PRODUCT
    # =========================================================
    for c in product_coupons:
        selected_products = random.sample(
            products,
            k=random.randint(1, 4)
        )

        for p in selected_products:
            db.session.add(
                CouponProduct(
                    coupon_id=c.id,
                    product_id=p.id
                )
            )

    db.session.commit()

    # =========================================================
    # 10. USER COUPON
    # =========================================================
    for u in users:
        for coupon in coupons[:3]:
            db.session.add(
                UserCoupon(
                    user_id=u.id,
                    coupon_id=coupon.id,
                    is_used=False
                )
            )

    db.session.commit()

    # =========================================================
    # 11. CART
    # =========================================================
    carts = []

    for u in users:
        cart = Cart(
            user_id=u.id,
            coupon_id=random.choice(coupons).id
        )

        carts.append(cart)

    db.session.add_all(carts)
    db.session.commit()

    # =========================================================
    # 12. CART ITEM
    # =========================================================
    for cart in carts:
        selected_products = random.sample(products, 3)

        for p in selected_products:
            db.session.add(
                CartItem(
                    cart_id=cart.id,
                    product_id=p.id,
                    quantity=random.randint(1, 3),
                    price=p.price
                )
            )

    db.session.commit()

    # =========================================================
    # 13. ORDERS
    # =========================================================
    orders = []

    for u in users:
        total_amount = random.randint(300000, 900000)
        discount_amount = random.randint(20000, 100000)

        final_amount = total_amount - discount_amount

        order = Order(
            user_id=u.id,
            coupon_id=random.choice(coupons).id,

            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,

            status=OrderStatus.COMPLETED
        )

        orders.append(order)

    db.session.add_all(orders)
    db.session.commit()

    # =========================================================
    # 14. ORDER ITEM
    # =========================================================
    sample_notes = [
        None,
        "Gọi trước khi giao",
        "Đóng gói cẩn thận",
        "Không gọi buổi trưa"
    ]

    for o in orders:
        selected_products = random.sample(products, 2)

        for p in selected_products:
            db.session.add(
                OrderItem(
                    order_id=o.id,
                    product_id=p.id,
                    quantity=random.randint(1, 3),
                    price=p.price,
                    note=random.choice(sample_notes)
                )
            )

    db.session.commit()

    print("✅ Seed data thành công!")


if __name__ == "__main__":
    with app.app_context():
        seed_data()
        seed_data()