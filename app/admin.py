import os
import uuid
from datetime import datetime

from flask import redirect, url_for, request, flash
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme
from flask_login import current_user, logout_user
from sqlalchemy import desc, func
from werkzeug.utils import secure_filename

from app import app, db
from app.models import (
    User, UserRole,
    Category, Product, ProductDetail,
    Cart, CartItem,
    CouponType, Coupon, CouponCategory, UserCoupon,
    Order, OrderItem,
    DiscountKind, CouponApplyType, CouponTargetType, CouponStatus, CouponCondition, CouponProduct, ProductImage
)
from app.dao import get_coupon_condition, get_usage_text, query_coupons_for_admin, get_coupon_create_dependencies, \
    create_coupon_from_form, get_coupon_form_data, update_coupon_from_form, delete_coupon_by_id, \
    validate_user_form_data_for_admin, admin_reset_user_password


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login", next=request.url))
        return redirect(url_for("index"))

    @expose("/")
    def index(self):
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

        chart_labels = month_keys
        chart_revenue = [revenue_map.get(m, {}).get("revenue", 0) for m in month_keys]
        chart_orders = [revenue_map.get(m, {}).get("orders", 0) for m in month_keys]

        total_revenue = db.session.query(
            func.sum(Order.final_amount)
        ).filter(
            Order.status == "completed"
        ).scalar() or 0

        total_orders = Order.query.filter_by(status="completed").count()
        total_products = Product.query.count()
        active_products = Product.query.filter_by(active=True).count()
        total_stock = db.session.query(func.sum(Product.stock_quantity)).scalar() or 0

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

        product_labels = [p.name for p in top_products]
        product_revenue = [float(p.revenue or 0) for p in top_products]
        product_sold = [int(p.sold_quantity or 0) for p in top_products]

        return self.render(
            "admin/index.html",
            total_revenue=total_revenue,
            total_orders=total_orders,
            total_products=total_products,
            active_products=active_products,
            total_stock=total_stock,
            chart_labels=chart_labels,
            chart_revenue=chart_revenue,
            chart_orders=chart_orders,
            top_products=top_products,
            product_labels=product_labels,
            product_revenue=product_revenue,
            product_sold=product_sold
        )


class MyAdminLogoutView(BaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect(url_for("login"))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class UserAdminView(AuthenticatedView):
    list_template = "admin/user/user_list.html"
    create_template = "admin/user/user_create.html"
    edit_template = "admin/user/user_edit.html"

    column_list = ['id', 'name', 'username', 'email', 'phone', 'role', 'active', 'created_date']
    column_searchable_list = ['name', 'username', 'email', 'phone']
    column_filters = ['role', 'active']

    form_columns = [
        'name',
        'email',
        'phone',
        'address',
        'role',
        'active'
    ]

    def on_model_change(self, form, model, is_created):
        name = (form.name.data or "").strip()
        email = (form.email.data or "").strip()
        phone = (form.phone.data or "").strip()
        address = (form.address.data or "").strip()

        validate_user_form_data_for_admin(
            name=name,
            username=model.username,
            email=email,
            phone=phone,
            address=address,
            password="dummy123!",
            user_id=None if is_created else model.id,
            require_password=False
        )

        model.name = name
        model.email = email
        model.phone = phone
        model.address = address

    @expose("/reset-password/<int:user_id>", methods=["POST"])
    def reset_password_view(self, user_id):
        user = User.query.get_or_404(user_id)

        try:
            temp_password = admin_reset_user_password(user.id)
            flash(f"Đã reset mật khẩu cho {user.username}. Mật khẩu tạm thời: {temp_password}", "success")
        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
        except Exception:
            db.session.rollback()
            flash("Không thể reset mật khẩu cho user này.", "danger")

        return redirect(url_for(".edit_view", id=user_id))

    @expose("/")
    def index_view(self):
        page = request.args.get("page", 1, type=int)
        per_page = app.config["PAGE_SIZE"]
        search = (request.args.get("search") or "").strip()

        query = User.query

        if search:
            keyword = f"%{search}%"
            query = query.filter(
                (User.name.ilike(keyword)) |
                (User.username.ilike(keyword)) |
                (User.email.ilike(keyword)) |
                (User.phone.ilike(keyword))
            )

        query = query.order_by(User.id.desc())

        total = query.count()
        pages = (total + per_page - 1) // per_page if total > 0 else 1

        if page < 1:
            page = 1
        if page > pages:
            page = pages

        users = query.offset((page - 1) * per_page).limit(per_page).all()

        return self.render(
            self.list_template,
            data=users,
            count=total,
            current_page=page,
            pages=pages,
            has_prev=page > 1,
            has_next=page < pages,
            search=search
        )


class CategoryAdminView(AuthenticatedView):
    column_list = ['id', 'name', 'description', 'active', 'created_date']
    column_searchable_list = ['name']
    column_filters = ['active']


class ProductAdminView(AuthenticatedView):
    list_template = "admin/product/product_list.html"
    create_template = "admin/product/product_create.html"
    edit_template = "admin/product/product_edit.html"

    column_list = ['id', 'name', 'price', 'image', 'category', 'stock_quantity', 'active', 'created_date']
    column_searchable_list = ['name']
    column_filters = ['active', 'price']

    @expose("/")
    def index_view(self):
        page = request.args.get("page", 1, type=int)
        per_page = app.config.get("PAGE_SIZE", 6)

        search = (request.args.get("search") or "").strip()
        category_id = request.args.get("category_id", type=int)
        price_sort = (request.args.get("price_sort") or "").strip()
        stock_sort = (request.args.get("stock_sort") or "").strip()

        query = Product.query

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

        total = query.count()
        pages = (total + per_page - 1) // per_page if total > 0 else 1

        if page < 1:
            page = 1
        if page > pages:
            page = pages

        products = query.offset((page - 1) * per_page).limit(per_page).all()
        categories = Category.query.order_by(Category.name.asc()).all()

        return self.render(
            self.list_template,
            data=products,
            categories=categories,
            count=total,
            current_page=page,
            pages=pages,
            has_prev=page > 1,
            has_next=page < pages,
            search=search,
            category_id=category_id,
            price_sort=price_sort,
            stock_sort=stock_sort
        )

    @expose("/new/", methods=["GET", "POST"])
    def create_view(self):
        categories = Category.query.all()

        if request.method == "POST":
            try:
                image_files = request.files.getlist("image_files")
                saved_images = []

                for image_file in image_files:
                    if image_file and image_file.filename:
                        allowed_exts = {"png", "jpg", "jpeg", "webp"}
                        filename = secure_filename(image_file.filename)
                        ext = filename.rsplit(".", 1)[-1].lower()

                        if ext not in allowed_exts:
                            raise ValueError("Chỉ được tải lên file ảnh PNG, JPG, JPEG hoặc WEBP.")

                        upload_dir = os.path.join(app.root_path, "static", "uploads", "products")
                        os.makedirs(upload_dir, exist_ok=True)

                        new_filename = f"{uuid.uuid4().hex}.{ext}"
                        save_path = os.path.join(upload_dir, new_filename)
                        image_file.save(save_path)

                        saved_images.append(url_for("static", filename=f"uploads/products/{new_filename}"))

                description = (request.form.get("description") or "").strip()
                origin = (request.form.get("origin") or "").strip()
                warranty = (request.form.get("warranty") or "").strip()

                if not description:
                    raise ValueError("Vui lòng nhập mô tả sản phẩm.")

                if not origin:
                    raise ValueError("Vui lòng nhập xuất xứ sản phẩm.")

                if not warranty:
                    raise ValueError("Vui lòng nhập thông tin bảo hành.")
                p = Product(
                    name=request.form.get("name"),
                    price=float(request.form.get("price") or 0),
                    stock_quantity=int(request.form.get("stock_quantity") or 0),
                    cate_id=int(request.form.get("cate_id")),
                    image=saved_images[0] if saved_images else None,
                    active=bool(request.form.get("active"))
                )

                db.session.add(p)
                db.session.flush()

                for index, img in enumerate(saved_images):
                    db.session.add(ProductImage(
                        product_id=p.id,
                        image=img,
                        is_main=(index == 0)
                    ))

                detail = ProductDetail(
                    product_id=p.id,
                    description=(request.form.get("description") or "").strip(),
                    origin=(request.form.get("origin") or "").strip(),
                    warranty=(request.form.get("warranty") or "").strip()
                )

                db.session.add(detail)

                db.session.commit()

                flash("Tạo sản phẩm thành công!", "success")
                return redirect(url_for(".index_view"))

            except ValueError as e:
                db.session.rollback()
                flash(str(e), "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Lỗi: {e}", "danger")

        return self.render(
            self.create_template,
            categories=categories
        )

    @expose("/edit/<int:id>", methods=["GET", "POST"])
    def edit_view(self, id):
        product = Product.query.get_or_404(id)
        categories = Category.query.all()

        if request.method == "POST":
            try:
                product.name = request.form.get("name")
                product.price = float(request.form.get("price") or 0)
                product.stock_quantity = int(request.form.get("stock_quantity") or 0)
                product.cate_id = int(request.form.get("cate_id"))
                product.active = bool(request.form.get("active"))
                description = (request.form.get("description") or "").strip()
                origin = (request.form.get("origin") or "").strip()
                warranty = (request.form.get("warranty") or "").strip()

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

                allowed_exts = {"png", "jpg", "jpeg", "webp"}

                remove_ids = request.form.getlist("remove_image_ids")

                if remove_ids:
                    ProductImage.query.filter(
                        ProductImage.product_id == product.id,
                        ProductImage.id.in_(remove_ids)
                    ).delete(synchronize_session=False)

                # 2. Upload thêm
                image_files = request.files.getlist("image_files")

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

                        image_path = url_for("static", filename=f"uploads/products/{new_filename}")

                        db.session.add(ProductImage(
                            product_id=product.id,
                            image=image_path,
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
                flash("Cập nhật sản phẩm thành công!", "success")
                return redirect(url_for(".index_view"))

            except ValueError as e:
                db.session.rollback()
                flash(str(e), "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Lỗi: {e}", "danger")

        return self.render(
            self.edit_template,
            product=product,
            categories=categories
        )

    @expose("/delete/<int:id>", methods=["POST"])
    def delete_view(self, id):
        product = Product.query.get_or_404(id)

        try:
            has_order = OrderItem.query.filter_by(product_id=product.id).first()
            has_cart = CartItem.query.filter_by(product_id=product.id).first()

            if has_order or has_cart:
                product.active = False
                db.session.commit()
                flash("Sản phẩm đã phát sinh dữ liệu nên không xóa cứng. Đã chuyển sang trạng thái ẩn.", "warning")
                return redirect(url_for(".index_view"))

            CouponProduct.query.filter_by(product_id=product.id).delete(synchronize_session=False)
            ProductImage.query.filter_by(product_id=product.id).delete(synchronize_session=False)
            ProductDetail.query.filter_by(product_id=product.id).delete(synchronize_session=False)

            db.session.delete(product)
            db.session.commit()

            flash("Xóa sản phẩm thành công!", "success")


        except Exception:
            db.session.rollback()
            flash("Không thể xóa sản phẩm!", "danger")

        return redirect(url_for(".index_view"))


class ProductDetailAdminView(AuthenticatedView):
    column_list = ['id', 'product', 'origin', 'warranty']


class CouponAdminView(AuthenticatedView):
    list_template = "admin/coupon/coupon_list.html"
    create_template = "admin/coupon/coupon_create.html"
    edit_template = "admin/coupon/coupon_edit.html"

    form_columns = [
        'name',
        'code',
        'description',
        'discount_kind',
        'discount_value',
        'apply_type',
        'target_type',
        'status',
        'min_order_value',
        'max_discount_value',
        'quantity',
        'used_count',
        'start_date',
        'end_date',
        'coupon_type_id',
        'active'
    ]

    @expose("/")
    def index_view(self):
        page = request.args.get("page", 1, type=int)
        per_page = app.config["PAGE_SIZE"]

        all_coupons = query_coupons_for_admin(request.args)

        total = len(all_coupons)
        pages = (total + per_page - 1) // per_page if total > 0 else 1

        if page < 1:
            page = 1
        if page > pages:
            page = pages

        start = (page - 1) * per_page
        end = start + per_page
        coupons = all_coupons[start:end]

        return self.render(
            self.list_template,
            coupons=coupons,
            page=page,
            current_page=page,
            per_page=per_page,
            total=total,
            count=total,
            pages=pages,
            has_prev=page > 1,
            has_next=page < pages,
            q=request.args.get("q", ""),
            apply_type=request.args.get("apply_type", ""),
            condition=request.args.get("condition", ""),
            status=request.args.get("status", ""),
            created_date=request.args.get("created_date", ""),
            start_date=request.args.get("start_date", ""),
            get_coupon_condition=get_coupon_condition,
            get_usage_text=get_usage_text,
            CouponApplyType=CouponApplyType,
            CouponTargetType=CouponTargetType,
            CouponStatus=CouponStatus,
            CouponCondition=CouponCondition,
            DiscountKind=DiscountKind
        )

    @expose("/new/", methods=["GET", "POST"])
    def create_view(self):
        categories, products = get_coupon_create_dependencies()

        if request.method == "POST":
            try:
                create_coupon_from_form(request.form)
                flash("Tạo mã giảm giá thành công!", "success")
                return redirect(url_for(".index_view"))
            except ValueError as e:
                db.session.rollback()
                flash(str(e), "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Có lỗi xảy ra khi tạo mã: {e}", "danger")

        return self.render(
            self.create_template,
            categories=categories,
            products=products
        )

    @expose("/edit/<int:coupon_id>", methods=["GET", "POST"])
    def edit_view(self, coupon_id):
        coupon = Coupon.query.get_or_404(coupon_id)

        if request.method == "POST":
            form_data = get_coupon_form_data(request.form, coupon)

            try:
                update_coupon_from_form(coupon, form_data)
                flash("Thay đổi mã giảm giá thành công!", "success")
                return redirect(url_for(".index_view"))
            except ValueError as e:
                db.session.rollback()
                flash(str(e), "danger")
                return self.render(
                    self.edit_template,
                    model=coupon,
                    form_data=form_data,
                    can_edit_start_date=(coupon.start_date and coupon.start_date > datetime.now())
                )
            except Exception as e:
                db.session.rollback()
                flash(f"Có lỗi xảy ra khi cập nhật mã: {e}", "danger")
                return self.render(
                    self.edit_template,
                    model=coupon,
                    form_data=form_data,
                    can_edit_start_date=(coupon.start_date and coupon.start_date > datetime.now())
                )

        return self.render(
            self.edit_template,
            model=coupon,
            form_data=get_coupon_form_data(request.form, coupon),
            can_edit_start_date=(coupon.start_date and coupon.start_date > datetime.now())
        )

    @expose("/delete/<int:coupon_id>", methods=["POST"])
    def delete_coupon(self, coupon_id):
        try:
            delete_coupon_by_id(coupon_id)
            flash("Xóa mã giảm giá thành công!", "success")
        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
        except Exception:
            db.session.rollback()
            flash("Không thể xóa mã giảm giá này!", "danger")

        return redirect(url_for(".index_view"))


class OrderAdminView(AuthenticatedView):
    column_list = [
        'id', 'user', 'coupon',
        'total_amount', 'discount_amount', 'final_amount',
        'status', 'created_at'
    ]
    column_filters = ['status', 'created_at']


admin = Admin(
    app=app,
    name="Discount Admin",
    theme=Bootstrap4Theme(),
    index_view=MyAdminIndexView(url="/admin")
)

admin.add_view(UserAdminView(User, db.session, name="Người dùng"))
admin.add_view(CategoryAdminView(Category, db.session, name="Danh mục"))
admin.add_view(ProductAdminView(Product, db.session, name="Sản phẩm"))
admin.add_view(ProductDetailAdminView(ProductDetail, db.session, name="Chi tiết sản phẩm"))
admin.add_view(AuthenticatedView(Cart, db.session, name="Giỏ hàng"))
admin.add_view(AuthenticatedView(CartItem, db.session, name="Chi tiết giỏ hàng"))
admin.add_view(AuthenticatedView(CouponType, db.session, name="Loại mã giảm giá"))
admin.add_view(CouponAdminView(Coupon, db.session, name="Mã giảm giá"))
admin.add_view(AuthenticatedView(CouponCategory, db.session, name="Mã - danh mục"))
admin.add_view(AuthenticatedView(CouponProduct, db.session, name="Mã - sản phẩm"))
admin.add_view(AuthenticatedView(UserCoupon, db.session, name="Mã của user"))
admin.add_view(OrderAdminView(Order, db.session, name="Đơn hàng"))
admin.add_view(AuthenticatedView(OrderItem, db.session, name="Chi tiết đơn hàng"))
admin.add_view(MyAdminLogoutView(name="Đăng xuất", endpoint="admin_logout"))
