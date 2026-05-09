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
    validate_user_form_data_for_admin, admin_reset_user_password, get_admin_dashboard_stats, paginate_query, \
    query_users_for_admin, query_categories_for_admin, save_category_from_form, delete_category_by_id, \
    query_products_for_admin, create_product_from_form, update_product_from_form, delete_product_by_id, paginate_list, \
    get_recent_order_notifications, count_new_orders, get_order_detail_for_admin, query_orders_for_admin, \
    get_user_detail_for_admin, admin_create_user_from_form, toggle_admin_active_status


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
        stats = get_admin_dashboard_stats()
        recent_order_notifications = get_recent_order_notifications()
        new_order_count = count_new_orders()

        return self.render(
            "admin/index.html",
            recent_order_notifications=recent_order_notifications,
            new_order_count=new_order_count,
            **stats
        )


class UserAdminView(AuthenticatedView):
    list_template = "admin/user/user_list.html"
    create_template = "admin/user/user_create.html"
    details_template = "admin/user/user_detail.html"

    can_create = False
    can_edit = False
    can_delete = False

    @expose("/")
    def index_view(self):
        page = request.args.get("page", 1, type=int)
        search = (request.args.get("search") or "").strip()

        pagination = paginate_query(
            query_users_for_admin(search),
            page=page,
            page_size=app.config["PAGE_SIZE"]
        )

        return self.render(
            self.list_template,
            data=pagination["items"],
            count=pagination["total"],
            current_page=pagination["page"],
            pages=pagination["pages"],
            has_prev=pagination["has_prev"],
            has_next=pagination["has_next"],
            search=search
        )

    @expose("/new/", methods=["GET", "POST"])
    def create_view(self):
        if request.method == "POST":
            try:
                admin_create_user_from_form(request.form)
                flash("Tạo tài khoản thành công!", "success")
                return redirect(url_for(".index_view"))

            except ValueError as e:
                db.session.rollback()
                flash(str(e), "danger")

            except Exception as e:
                db.session.rollback()
                flash(f"Không thể tạo tài khoản: {e}", "danger")

        return self.render(self.create_template)

    @expose("/detail/<int:user_id>")
    def detail_view(self, user_id):
        detail = get_user_detail_for_admin(user_id)

        return self.render(
            self.details_template,
            user=detail["user"],
            stats=detail["stats"],
            recent_orders=detail["recent_orders"],
            current_coupons=detail["current_coupons"],
            used_coupons=detail["used_coupons"]
        )

    @expose("/toggle-active/<int:user_id>", methods=["POST"])
    def toggle_active_view(self, user_id):
        try:
            toggle_admin_active_status(user_id, current_user.id)
            flash("Cập nhật trạng thái admin thành công!", "success")

        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")

        except Exception:
            db.session.rollback()
            flash("Không thể cập nhật trạng thái tài khoản.", "danger")

        return redirect(url_for(".index_view"))


class CategoryAdminView(AuthenticatedView):
    list_template = "admin/category/category_manage.html"

    column_list = ['id', 'name', 'description', 'active', 'created_date']
    column_searchable_list = ['name']
    column_filters = ['active']

    @expose("/", methods=["GET"])
    def index_view(self):
        search = (request.args.get("search") or "").strip()
        selected_id = request.args.get("id", type=int)
        mode = request.args.get("mode", "view")

        categories = query_categories_for_admin(search)
        selected_category = Category.query.get(selected_id) if selected_id else None

        return self.render(
            self.list_template,
            categories=categories,
            selected_category=selected_category,
            search=search,
            mode=mode,
            count=len(categories)
        )

    @expose("/save/", methods=["POST"])
    def save_category(self):
        category_id = request.form.get("id", type=int)
        name = request.form.get("name")
        description = request.form.get("description")
        active = bool(request.form.get("active"))

        try:
            save_category_from_form(
                category_id=category_id,
                name=name,
                description=description,
                active=active
            )

            if category_id:
                flash("Cập nhật danh mục thành công!", "success")
            else:
                flash("Tạo danh mục thành công!", "success")

        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Không thể lưu danh mục: {e}", "danger")

        return redirect(url_for(".index_view"))

    @expose("/delete/<int:id>", methods=["POST"])
    def delete_view(self, id):
        try:
            result = delete_category_by_id(id)

            if result == "soft_delete":
                flash("Danh mục đã có sản phẩm nên không xóa cứng. Đã chuyển sang trạng thái ẩn.", "warning")
            else:
                flash("Xóa danh mục thành công!", "success")

        except Exception:
            db.session.rollback()
            flash("Không thể xóa danh mục này.", "danger")

        return redirect(url_for(".index_view"))


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

        query = query_products_for_admin(
            search=search,
            category_id=category_id,
            price_sort=price_sort,
            stock_sort=stock_sort
        )

        pagination = paginate_query(
            query=query,
            page=page,
            page_size=per_page
        )

        categories = Category.query.order_by(Category.name.asc()).all()

        return self.render(
            self.list_template,
            data=pagination["items"],
            categories=categories,
            count=pagination["total"],
            current_page=pagination["page"],
            pages=pagination["pages"],
            has_prev=pagination["has_prev"],
            has_next=pagination["has_next"],
            search=search,
            category_id=category_id,
            price_sort=price_sort,
            stock_sort=stock_sort
        )

    @expose("/new/", methods=["GET", "POST"])
    def create_view(self):
        categories = Category.query.order_by(Category.name.asc()).all()

        if request.method == "POST":
            try:
                create_product_from_form(
                    form=request.form,
                    files=request.files
                )

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
        categories = Category.query.order_by(Category.name.asc()).all()

        if request.method == "POST":
            try:
                update_product_from_form(
                    product=product,
                    form=request.form,
                    files=request.files
                )

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
        try:
            result = delete_product_by_id(id)

            if result == "soft_delete":
                flash(
                    "Sản phẩm đã phát sinh dữ liệu nên không xóa cứng. Đã chuyển sang trạng thái ẩn.",
                    "warning"
                )
            else:
                flash("Xóa sản phẩm thành công!", "success")

        except Exception:
            db.session.rollback()
            flash("Không thể xóa sản phẩm!", "danger")

        return redirect(url_for(".index_view"))


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

        pagination = paginate_list(
            items=all_coupons,
            page=page,
            page_size=per_page
        )

        return self.render(
            self.list_template,
            coupons=pagination["items"],
            page=pagination["page"],
            current_page=pagination["page"],
            per_page=per_page,
            total=pagination["total"],
            count=pagination["total"],
            pages=pagination["pages"],
            has_prev=pagination["has_prev"],
            has_next=pagination["has_next"],
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
        categories, products, coupon_types = get_coupon_create_dependencies()

        if request.method == "POST":
            try:
                create_coupon_from_form(request.form)

                flash("Tạo mã giảm giá thành công!", "coupon_success")
                return redirect(url_for(".index_view"))

            except ValueError as e:
                db.session.rollback()
                flash(str(e), "coupon_danger")

            except Exception as e:
                db.session.rollback()
                flash(f"Có lỗi xảy ra khi tạo mã: {e}", "coupon_danger")

        return self.render(
            self.create_template,
            categories=categories,
            products=products,
            coupon_types=coupon_types
        )

    @expose("/edit/<int:coupon_id>", methods=["GET", "POST"])
    def edit_view(self, coupon_id):
        coupon = Coupon.query.get_or_404(coupon_id)

        if request.method == "POST":
            form_data = get_coupon_form_data(request.form, coupon)

            try:
                update_coupon_from_form(coupon, form_data)

                flash("Thay đổi mã giảm giá thành công!", "coupon_success")
                return redirect(url_for(".index_view"))

            except ValueError as e:
                db.session.rollback()
                flash(str(e), "coupon_danger")

                return self.render(
                    self.edit_template,
                    model=coupon,
                    form_data=form_data,
                    can_edit_start_date=(coupon.start_date and coupon.start_date > datetime.now())
                )

            except Exception as e:
                db.session.rollback()
                flash(f"Có lỗi xảy ra khi cập nhật mã: {e}", "coupon_danger")

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
            flash("Xóa mã giảm giá thành công!", "coupon_success")

        except ValueError as e:
            db.session.rollback()
            flash(str(e), "coupon_danger")

        except Exception:
            db.session.rollback()
            flash("Không thể xóa mã giảm giá này!", "coupon_danger")

        return redirect(url_for(".index_view"))


class OrderAdminView(AuthenticatedView):
    list_template = "admin/order/order_list.html"
    details_template = "admin/order/order_detail.html"

    @expose("/")
    def index_view(self):
        page = request.args.get("page", 1, type=int)
        search = request.args.get("search", "")

        pagination = paginate_query(
            query_orders_for_admin(search),
            page=page,
            page_size=app.config["PAGE_SIZE"]
        )

        return self.render(
            self.list_template,
            orders=pagination["items"],
            count=pagination["total"],
            current_page=pagination["page"],
            pages=pagination["pages"],
            has_prev=pagination["has_prev"],
            has_next=pagination["has_next"],
            search=search
        )

    @expose("/detail/<int:order_id>")
    def detail_view(self, order_id):
        order = get_order_detail_for_admin(order_id)
        return self.render(
            self.details_template,
            order=order
        )


admin = Admin(
    app=app,
    name="Discount Admin",
    theme=Bootstrap4Theme(),
    index_view=MyAdminIndexView(url="/admin")
)

admin.add_view(UserAdminView(User, db.session, name="Người dùng"))
admin.add_view(CategoryAdminView(Category, db.session, name="Danh mục"))
admin.add_view(ProductAdminView(Product, db.session, name="Sản phẩm"))
admin.add_view(CouponAdminView(Coupon, db.session, name="Mã giảm giá"))
admin.add_view(OrderAdminView(Order, db.session, name="Đơn hàng", endpoint="order"))
