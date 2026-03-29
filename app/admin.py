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
from app.dao import get_coupon_condition, get_usage_text


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
    column_list = ['id', 'name', 'username', 'email', 'phone', 'role', 'active', 'created_date']
    column_searchable_list = ['name', 'username', 'email', 'phone']
    column_filters = ['role', 'active']


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

    def _parse_datetime_local(self, value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%d/%m/%Y %H:%M")
        except ValueError:
            return None

    def _to_int_list(self, values):
        result = []
        for v in values:
            try:
                result.append(int(v))
            except (TypeError, ValueError):
                continue
        return result
    def _get_coupon_form_data(self, coupon=None):
        return {
            "name": request.form.get("name", coupon.name if coupon else "").strip() if request.method == "POST" else (coupon.name if coupon else ""),
            "code": request.form.get("code", coupon.code if coupon else "").strip().upper() if request.method == "POST" else (coupon.code if coupon else ""),
            "description": request.form.get("description", coupon.description if coupon else "").strip() if request.method == "POST" else (coupon.description if coupon else ""),
            "discount_kind": request.form.get(
                "discount_kind",
                coupon.discount_kind.value if coupon and coupon.discount_kind else "fixed"
            ),
            "discount_value": request.form.get(
                "discount_value",
                coupon.discount_value if coupon else ""
            ),
            "max_discount_value": request.form.get(
                "max_discount_value",
                coupon.max_discount_value if coupon and coupon.max_discount_value is not None else ""
            ),
            "min_order_value": request.form.get(
                "min_order_value",
                coupon.min_order_value if coupon else ""
            ),
            "quantity": request.form.get(
                "quantity",
                coupon.quantity if coupon else ""
            ),
            "used_count": coupon.used_count if coupon else 0,
            "start_date": request.form.get(
                "start_date",
                coupon.start_date.strftime("%d/%m/%Y %H:%M") if coupon and coupon.start_date else ""
            ),
            "end_date": request.form.get(
                "end_date",
                coupon.end_date.strftime("%d/%m/%Y %H:%M") if coupon and coupon.end_date else ""
            ),
            "status": request.form.get(
                "status",
                coupon.status.name if coupon and coupon.status else "ACTIVE"
            ),
        }
    def _build_query(self):
        query = Coupon.query

        q = request.args.get("q", "").strip()
        apply_type = request.args.get("apply_type", "").strip()
        condition = request.args.get("condition", "").strip()
        status = request.args.get("status", "").strip()
        created_date = request.args.get("created_date", "").strip()
        start_date = request.args.get("start_date", "").strip()

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
            coupons = [
                c for c in coupons
                if get_coupon_condition(c).value == condition
            ]

        return coupons

    @expose("/")
    def index_view(self):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        all_coupons = self._build_query()

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
        categories = Category.query.filter_by(active=True).order_by(Category.name.asc()).all()
        products = Product.query.filter_by(active=True) \
            .order_by(Product.stock_quantity.desc(), Product.name.asc()) \
            .all()

        if request.method == "POST":
            try:
                name = request.form.get("name", "").strip()
                code = request.form.get("code", "").strip().upper()
                description = request.form.get("description", "").strip()

                discount_kind_raw = request.form.get("discount_kind", "fixed")
                apply_scope = request.form.get("apply_scope", "all_product")
                target_type_raw = request.form.get("target_type", "all")
                max_discount_value = request.form.get("max_discount_value")
                max_discount_value = float(max_discount_value) if max_discount_value else None
                discount_value = float(request.form.get("discount_value") or 0)
                min_order_value = float(request.form.get("min_order_value") or 0)
                quantity = int(request.form.get("quantity") or 0)

                start_date = self._parse_datetime_local(request.form.get("start_date"))
                end_date = self._parse_datetime_local(request.form.get("end_date"))

                usage_limit_type = request.form.get("usage_limit_type", "many")
                show_public = bool(request.form.get("show_public"))

                category_ids = self._to_int_list(request.form.getlist("category_ids"))
                product_ids = self._to_int_list(request.form.getlist("product_ids"))
                print("discount_kind_raw =", request.form.get("discount_kind"))
                print("discount_kind_list =", request.form.getlist("discount_kind"))
                print("FORM DATA =", request.form)
                if not name:
                    raise ValueError("Vui lòng nhập tên mã giảm giá.")

                if not code:
                    raise ValueError("Vui lòng nhập code mã giảm giá.")

                if Coupon.query.filter(Coupon.code == code).first():
                    raise ValueError("Code mã giảm giá đã tồn tại.")

                if discount_value <= 0:
                    raise ValueError("Mức giảm phải lớn hơn 0.")

                if discount_kind_raw == "percentage" and discount_value > 50:
                    raise ValueError("Mã giảm theo % không được vượt quá 50%.")

                if quantity < 0:
                    raise ValueError("Số lượt sử dụng không hợp lệ.")

                if start_date and end_date and start_date > end_date:
                    raise ValueError("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc.")

                if apply_scope == "selected_category" and not category_ids:
                    raise ValueError("Bạn phải chọn ít nhất 1 ngành hàng.")

                if apply_scope == "selected_product" and not product_ids:
                    raise ValueError("Bạn phải chọn ít nhất 1 sản phẩm.")

                discount_kind = (
                    DiscountKind.PERCENTAGE
                    if discount_kind_raw == "percentage"
                    else DiscountKind.FIXED )

                target_type = (
                    CouponTargetType.LOYAL_1Y
                    if target_type_raw == "old_customer"
                    else CouponTargetType.ALL
                )

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
                        db.session.add(CouponCategory(
                            coupon_id=coupon.id,
                            category_id=cate_id
                        ))

                if apply_type == CouponApplyType.PRODUCT:
                    for product_id in product_ids:
                        db.session.add(CouponProduct(
                            coupon_id=coupon.id,
                            product_id=product_id
                        ))

                db.session.commit()
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
            form_data = self._get_coupon_form_data(coupon)

            try:
                name = form_data["name"]
                code = form_data["code"]
                description = form_data["description"]

                discount_kind_raw = form_data["discount_kind"]
                discount_value = float(form_data["discount_value"] or 0)
                min_order_value = float(form_data["min_order_value"] or 0)
                quantity = int(form_data["quantity"] or 0)

                max_discount_value_raw = form_data["max_discount_value"]
                max_discount_value = float(max_discount_value_raw) if str(max_discount_value_raw).strip() != "" else None

                start_date = self._parse_datetime_local(form_data["start_date"])
                end_date = self._parse_datetime_local(form_data["end_date"])

                status_raw = form_data["status"]

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

                if quantity < 0:
                    raise ValueError("Số lượng không hợp lệ.")

                if min_order_value < 0:
                    raise ValueError("Giá trị đơn tối thiểu không hợp lệ.")

                if start_date and end_date and start_date > end_date:
                    raise ValueError("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc.")

                discount_kind = (
                    DiscountKind.PERCENTAGE
                    if discount_kind_raw == "percentage"
                    else DiscountKind.FIXED
                )

                status = (
                    CouponStatus.INACTIVE
                    if status_raw == "INACTIVE"
                    else CouponStatus.ACTIVE
                )

                coupon.name = name
                coupon.code = code
                coupon.description = description
                coupon.discount_kind = discount_kind
                coupon.discount_value = discount_value
                coupon.min_order_value = min_order_value
                coupon.quantity = quantity
                coupon.max_discount_value = max_discount_value if discount_kind == DiscountKind.PERCENTAGE else None
                coupon.start_date = start_date
                coupon.end_date = end_date
                coupon.status = status

                db.session.commit()
                flash("Thay đổi mã giảm giá thành công!", "success")
                return redirect(url_for(".index_view"))

            except ValueError as e:
                db.session.rollback()
                flash(str(e), "danger")
                return self.render(
                    self.edit_template,
                    model=coupon,
                    form_data=form_data
                )

            except Exception as e:
                db.session.rollback()
                flash(f"Có lỗi xảy ra khi cập nhật mã: {e}", "danger")
                return self.render(
                    self.edit_template,
                    model=coupon,
                    form_data=form_data
                )

        return self.render(
            self.edit_template,
            model=coupon,
            form_data=self._get_coupon_form_data(coupon)
        )
    @expose("/delete/<int:coupon_id>", methods=["POST"])
    def delete_coupon(self, coupon_id):
        coupon = Coupon.query.get_or_404(coupon_id)

        try:
            db.session.delete(coupon)
            db.session.commit()
            flash("Xóa mã giảm giá thành công!", "success")
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