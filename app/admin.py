from datetime import datetime

from flask import redirect, url_for, request, flash
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme
from flask_login import current_user, logout_user

from app import app, db
from app.models import (
    User, UserRole,
    Category, Product, ProductDetail,
    Cart, CartItem,
    CouponType, Coupon, CouponCategory, UserCoupon,
    Order, OrderItem,
    DiscountKind, CouponApplyType, CouponTargetType, CouponStatus, CouponCondition, CouponProduct
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
        return self.render("admin/index.html")


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
    column_list = ['id', 'name', 'price', 'image', 'category', 'active', 'created_date']
    column_searchable_list = ['name']
    column_filters = ['active', 'price']


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
        per_page = request.args.get("per_page", 10, type=int)

        all_coupons = query_coupons_for_admin(request.args)

        total = len(all_coupons)
        start = (page - 1) * per_page
        end = start + per_page
        coupons = all_coupons[start:end]

        return self.render(
            self.list_template,
            coupons=coupons,
            page=page,
            per_page=per_page,
            total=total,
            pages=(total + per_page - 1) // per_page,
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
