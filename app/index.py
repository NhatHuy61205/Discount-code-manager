import app.admin
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.dao import (
    auth_user, get_active_products, register_user,
    get_best_coupon_for_product, get_product_by_id,
    get_cart_items_by_user, get_suggested_products, stats_cart_db, get_or_create_cart, get_public_coupons_for_user,
    get_my_coupons, save_coupon_for_user, get_used_coupons, get_apply_type_text, get_coupon_condition,
    get_remaining_quantity, get_available_my_coupons_for_cart, validate_selected_coupon_for_cart,
    get_default_address_for_user, get_addresses_by_user, update_user_address, create_order_from_checkout,
    get_orders_by_user, get_recommended_products, add_product_to_cart, update_cart_item_quantity,
    delete_cart_item_by_product, get_top_categories_by_product_count, create_user_address
)
from app.models import UserRole, Order, CartItem


@app.route("/")
def index():
    if current_user.is_authenticated and current_user.role == UserRole.ADMIN:
        return redirect(url_for("admin.index"))

    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "", type=str).strip()

    hero_banners = [f"pics/pics_sale{i}.jpg" for i in range(1, 5)]
    product_data = get_active_products(page=page, q=q)

    return render_template(
        "index.html",
        hero_banners=hero_banners,
        products=product_data["items"],
        current_page=product_data["page"],
        pages=product_data["pages"],
        has_next=product_data["has_next"],
        q=q
    )


@app.route("/search")
def search_products():
    if current_user.is_authenticated and current_user.role == UserRole.ADMIN:
        return redirect(url_for("admin.index"))

    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("keyword", "", type=str).strip()

    if not keyword:
        return redirect(url_for("welcome_package"))

    product_data = get_active_products(page=page, q=keyword)

    return render_template(
        "search.html",
        products=product_data["items"],
        current_page=product_data["page"],
        pages=product_data["pages"],
        total=product_data["total"],
        has_next=product_data["has_next"],
        has_prev=product_data["has_prev"],
        keyword=keyword
    )


@app.route("/welcome-package")
def welcome_package():
    if current_user.is_authenticated and current_user.role == UserRole.ADMIN:
        return redirect(url_for("admin.index"))

    categories = get_top_categories_by_product_count(limit=3)

    return render_template(
        "welcome_package.html",
        categories=categories
    )


@app.route("/api/products")
def load_more_products():
    page = request.args.get("page", 1, type=int)
    product_data = get_active_products(page=page)

    return jsonify({
        "success": True,
        "products": [
            {
                "id": product.id,
                "name": product.name,
                "image": product.image or "https://via.placeholder.com/600x400?text=No+Image",
                "description": (
                    product.product_detail.description
                    if product.product_detail and product.product_detail.description
                    else "Chưa có mô tả cho sản phẩm này."
                ),
                "price": "{:,.0f}".format(product.price).replace(",", ".") + "đ",
                "detail_url": url_for("product_detail", product_id=product.id),
                "requires_login": not current_user.is_authenticated
            }
            for product in product_data["items"]
        ],
        "current_page": product_data["page"],
        "has_next": product_data["has_next"]
    })


@app.context_processor
def inject_cart_preview_data():
    cart_count = 0
    cart_preview_items = []
    cart_preview_total = 0

    if current_user.is_authenticated and current_user.role != UserRole.ADMIN:
        cart = get_or_create_cart(current_user)
        cart_stats = stats_cart_db(cart)

        cart_count = cart_stats.get("total_items", 0)
        cart_preview_total = cart_stats.get("total_quantity", 0)

        cart_items = get_cart_items_by_user(current_user)
        cart_preview_items = cart_items[:5]

    return {
        "cart_count": cart_count,
        "cart_preview_items": cart_preview_items,
        "cart_preview_total": cart_preview_total
    }


@app.route("/login", methods=["GET", "POST"])
def login():
    err_msg = None

    if current_user.is_authenticated:
        if current_user.role.name == "ADMIN":
            return redirect(url_for("admin.index"))
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")

            if not username or not password:
                raise ValueError("Vui lòng nhập đầy đủ thông tin")

            user = auth_user(username=username, password=password)

            if user:
                login_user(user)

                if user.role.name == "ADMIN":
                    return redirect(url_for("admin.index"))

                return redirect(url_for("index"))
            else:
                raise ValueError("Sai tài khoản hoặc mật khẩu")

        except Exception as e:
            err_msg = str(e)

    return render_template("login.html", error=err_msg)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    err_msg = None
    form_data = {}

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        form_data = request.form.to_dict()

        try:
            register_user(
                name=request.form.get("name"),
                username=request.form.get("username"),
                email=request.form.get("email"),
                phone=request.form.get("phone"),
                address=request.form.get("address"),
                password=request.form.get("password"),
                confirm=request.form.get("confirm"),
            )
            return redirect(url_for("login"))
        except Exception as e:
            err_msg = str(e)

    return render_template(
        "register.html",
        error=err_msg,
        form_data=form_data
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)
    best_coupon, best_discount = get_best_coupon_for_product(product)

    return render_template(
        "product_detail.html",
        product=product,
        best_coupon=best_coupon,
        best_discount=best_discount,
    )


# CART
@app.route("/cart")
@login_required
def cart():
    cart_items = get_cart_items_by_user(current_user)
    suggested_products = get_suggested_products(10)
    my_coupons = get_my_coupons(current_user)

    return render_template(
        "cart.html",
        cart_items=cart_items,
        suggested_products=suggested_products,
        my_coupons=my_coupons,
        get_coupon_condition=get_coupon_condition,
        get_apply_type_text=get_apply_type_text
    )


@app.route("/api/cart/available-coupons", methods=["POST"])
@login_required
def get_cart_available_coupons():
    try:
        data = request.get_json() or {}
        selected_product_ids = data.get("selected_product_ids", [])

        coupons = get_available_my_coupons_for_cart(current_user, selected_product_ids)

        return jsonify({
            "success": True,
            "message": "Lấy danh sách mã giảm giá thành công",
            "coupons": coupons
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "coupons": []
        }), 400
    except Exception:
        return jsonify({
            "success": False,
            "message": "Không thể tải danh sách mã giảm giá",
            "coupons": []
        }), 500


@app.route("/api/cart/apply-coupon", methods=["POST"])
@login_required
def apply_coupon_to_cart():
    try:
        data = request.get_json() or {}
        coupon_id = data.get("coupon_id")

        if not coupon_id:
            raise ValueError("Thiếu mã giảm giá")

        coupon_id = int(coupon_id)
        selected_product_ids = data.get("selected_product_ids", [])

        result = validate_selected_coupon_for_cart(
            current_user,
            coupon_id,
            selected_product_ids
        )

        return jsonify({
            "success": True,
            "message": "Áp dụng mã giảm giá thành công",
            "coupon": result
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception:
        return jsonify({
            "success": False,
            "message": "Không thể áp dụng mã giảm giá"
        }), 500


@app.route('/api/carts', methods=['POST'])
@login_required
def add_to_cart():
    try:
        data = request.get_json() or {}
        product_id = data.get("id")

        result = add_product_to_cart(
            current_user,
            product_id=product_id,
            quantity=data.get("quantity", 1)
        )

        product = get_product_by_id(product_id)

        result["item"] = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "image": product.image or "https://via.placeholder.com/80x80?text=No+Image",
            "url": url_for("product_detail", product_id=product.id)
        }

        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Không thể thêm sản phẩm vào giỏ hàng"}), 500


@app.route('/api/carts/<int:product_id>', methods=['PUT'])
@login_required
def update_cart(product_id):
    try:
        data = request.get_json() or {}
        result = update_cart_item_quantity(
            current_user,
            product_id,
            data.get("quantity", 1)
        )
        return jsonify(result)
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        product = get_product_by_id(product_id)

        return jsonify({
            "error": str(e),
            "max_quantity": product.stock_quantity
        }), 400
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Không thể cập nhật giỏ hàng"}), 500


@app.route('/api/carts/<int:product_id>', methods=['DELETE'])
@login_required
def delete_cart_item(product_id):
    try:
        result = delete_cart_item_by_product(current_user, product_id)
        return jsonify(result)
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Không thể xóa sản phẩm khỏi giỏ hàng"}), 500


# RECOMMEND
@app.route("/recommend")
def recommend():
    page = request.args.get("page", 1, type=int)
    product_data = get_recommended_products(page=page)

    return render_template(
        "recommend.html",
        products=product_data["items"],
        current_page=product_data["page"],
        pages=product_data["pages"],
        has_prev=product_data["has_prev"],
        has_next=product_data["has_next"]
    )


# Mua lại
@app.route('/api/orders/<int:order_id>/rebuy', methods=['POST'])
@login_required
def rebuy_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()

    if not order:
        return jsonify({"message": "Không tìm thấy đơn hàng"}), 404

    if not order.order_items:
        return jsonify({"message": "Đơn hàng không có sản phẩm"}), 400

    cart = get_or_create_cart(current_user)

    added_any = False
    warning_messages = []

    for order_item in order.order_items:
        product = order_item.product
        product_name = (
            product.name if product and product.name else f"Sản phẩm #{order_item.product_id}"
        )

        if not product:
            warning_messages.append(f"{product_name} không còn tồn tại.")
            continue

        if not product.active:
            warning_messages.append(f"{product_name} hiện không còn được kinh doanh.")
            continue

        if product.stock_quantity <= 0:
            warning_messages.append(f"{product_name} đã hết hàng.")
            continue

        qty = int(order_item.quantity or 0)
        if qty <= 0:
            warning_messages.append(f"{product_name} có số lượng mua lại không hợp lệ.")
            continue

        existing = None
        for ci in cart.cart_items:
            if ci.product_id == product.id:
                existing = ci
                break

        if existing:
            remain = max(product.stock_quantity - existing.quantity, 0)

            if remain <= 0:
                warning_messages.append(
                    f"{product_name} không thể thêm thêm vì giỏ hàng đã đạt tối đa theo tồn kho."
                )
                continue

            add_qty = min(qty, remain)

            if add_qty < qty:
                warning_messages.append(
                    f"{product_name} chỉ thêm được {add_qty}/{qty} sản phẩm do giới hạn tồn kho."
                )

            existing.quantity += add_qty
            added_any = True
        else:
            add_qty = min(qty, product.stock_quantity)

            if add_qty <= 0:
                warning_messages.append(f"{product_name} đã hết hàng.")
                continue

            if add_qty < qty:
                warning_messages.append(
                    f"{product_name} chỉ thêm được {add_qty}/{qty} sản phẩm do giới hạn tồn kho."
                )

            item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=add_qty,
                price=product.price
            )
            db.session.add(item)
            added_any = True

    if not added_any:
        return jsonify({
            "message": "Không thể mua lại đơn hàng.",
            "warning_messages": warning_messages if warning_messages else [
                "Tất cả sản phẩm trong đơn hiện không thể thêm vào giỏ hàng."
            ]
        }), 400

    db.session.commit()

    return jsonify({
        "message": "Đã thêm sản phẩm có thể mua lại vào giỏ hàng.",
        "warning_messages": warning_messages,
        "redirect_url": url_for("cart")
    }), 200


@app.route("/coupon")
@login_required
def coupon_page():
    public_coupons = get_public_coupons_for_user(current_user)
    my_coupons = get_my_coupons(current_user)
    used_coupons = get_used_coupons(current_user)

    return render_template(
        "coupon.html",
        public_coupons=public_coupons,
        my_coupons=my_coupons,
        used_coupons=used_coupons,
        get_apply_type_text=get_apply_type_text,
        get_coupon_condition=get_coupon_condition,
        get_remaining_quantity=get_remaining_quantity
    )


@app.route("/coupon/save/<int:coupon_id>", methods=["POST"])
@login_required
def save_coupon(coupon_id):
    from flask import flash

    try:
        save_coupon_for_user(current_user, coupon_id)
        flash("Lưu mã giảm giá thành công!", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("coupon_page"))


# Thanh Toán
@app.route("/checkout")
@login_required
def checkout():
    selected_product_ids = request.args.getlist("selected_product_ids", type=int)
    coupon_id = request.args.get("coupon_id", type=int)
    # coupon_code = request.args.get("coupon_code", default="", type=str)
    # discount_amount = request.args.get("discount_amount", default=0, type=float)

    if not selected_product_ids:
        return redirect(url_for("cart"))

    cart_items = get_cart_items_by_user(current_user)
    selected_items = [item for item in cart_items if item.product_id in selected_product_ids]

    if not selected_items:
        return redirect(url_for("cart"))

    shipping_address = get_default_address_for_user(current_user)
    addresses = get_addresses_by_user(current_user)

    selected_coupon = None
    if coupon_id:
        selected_coupon = validate_selected_coupon_for_cart(
            current_user,
            coupon_id,
            selected_product_ids
        )

    return render_template(
        "checkout.html",
        shipping_address=shipping_address,
        addresses=addresses,
        checkout_items=selected_items,
        selected_product_ids=selected_product_ids,
        selected_coupon=selected_coupon
    )


@app.route("/api/checkout/address/<int:address_id>", methods=["PUT"])
@login_required
def update_checkout_address(address_id):
    try:
        data = request.get_json() or {}

        updated_address = update_user_address(
            current_user,
            address_id=address_id,
            recipient_name=data.get("recipient_name"),
            phone=data.get("phone"),
            address_line=data.get("address_line"),
            set_as_default=bool(data.get("set_as_default"))
        )

        return jsonify({
            "success": True,
            "message": "Cập nhật địa chỉ thành công",
            "address": updated_address
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        print("UPDATE ADDRESS ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Không thể cập nhật địa chỉ"
        }), 500


@app.route("/api/checkout/address", methods=["POST"])
@login_required
def create_checkout_address():
    try:
        data = request.get_json() or {}

        address = create_user_address(
            current_user,
            recipient_name=data.get("recipient_name"),
            phone=data.get("phone"),
            address_line=data.get("address_line"),
            set_as_default=data.get("set_as_default", False)
        )

        return jsonify({
            "success": True,
            "message": "Thêm địa chỉ thành công",
            "address": address
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Không thể thêm địa chỉ"
        }), 500


@app.route("/api/checkout/place-order", methods=["POST"])
@login_required
def place_order():
    try:
        data = request.get_json() or {}

        selected_product_ids = data.get("selected_product_ids", [])
        coupon_id = data.get("coupon_id")
        notes = data.get("notes", {})

        order = create_order_from_checkout(
            user=current_user,
            selected_product_ids=selected_product_ids,
            coupon_id=coupon_id,
            notes=notes
        )

        return jsonify({
            "success": True,
            "message": "Đặt hàng thành công",
            "order_id": order.id,
            "redirect_url": url_for("index", order_success=1)
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        print("PLACE ORDER ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Không thể đặt hàng"
        }), 500


# order
@app.route("/my-orders")
@login_required
def my_orders():
    orders = get_orders_by_user(current_user)

    return render_template(
        "my_orders.html",
        orders=orders
    )


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
