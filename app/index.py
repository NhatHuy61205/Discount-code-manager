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
    get_default_address_for_user, get_addresses_by_user, update_user_address
)
from app.models import UserRole


@app.route("/")
def index():
    if current_user.is_authenticated and current_user.role == UserRole.ADMIN:
        return redirect(url_for("admin.index"))

    hero_banners = [f"pics/pics_sale{i}.jpg" for i in range(1, 5)]
    products = get_active_products()

    return render_template(
        "index.html",
        hero_banners=hero_banners,
        products=products
    )


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

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
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

    return render_template("register.html", error=err_msg)


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
        coupon_id = int(data.get("coupon_id"))
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
    cart = get_or_create_cart(current_user)

    product_id = request.json.get('id')
    quantity = int(request.json.get('quantity', 1))

    product = get_product_by_id(product_id)

    if quantity <= 0:
        return jsonify({"error": "Số lượng phải lớn hơn 0"}), 400

    if product.stock_quantity <= 0:
        return jsonify({"error": "Sản phẩm đã hết hàng"}), 400

    item = None
    for i in cart.cart_items:
        if i.product_id == product.id:
            item = i
            break

    if item:
        if item.quantity + quantity > product.stock_quantity:
            return jsonify({
                "error": f"Chỉ còn {product.stock_quantity} sản phẩm trong kho"
            }), 400

        item.quantity += quantity
    else:
        if quantity > product.stock_quantity:
            return jsonify({
                "error": f"Chỉ còn {product.stock_quantity} sản phẩm trong kho"
            }), 400

        from app.models import CartItem
        item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price
        )
        db.session.add(item)

    db.session.commit()

    return jsonify(stats_cart_db(cart))


@app.route('/api/carts/<int:product_id>', methods=['PUT'])
@login_required
def update_cart(product_id):
    cart = get_or_create_cart(current_user)

    quantity = int(request.json.get("quantity", 1))
    product = get_product_by_id(product_id)

    if quantity <= 0:
        return jsonify({"error": "Số lượng phải lớn hơn 0"}), 400

    if quantity > product.stock_quantity:
        return jsonify({
            "error": f"Chỉ còn {product.stock_quantity} sản phẩm trong kho"
        }), 400

    item = None
    for i in cart.cart_items:
        if i.product_id == product.id:
            item = i
            break

    if not item:
        return jsonify({"error": "Sản phẩm không có trong giỏ hàng"}), 404

    item.quantity = quantity
    db.session.commit()

    return jsonify(stats_cart_db(cart))


@app.route('/api/carts/<int:product_id>', methods=['DELETE'])
@login_required
def delete_cart_item(product_id):
    cart = get_or_create_cart(current_user)

    item = None
    for i in cart.cart_items:
        if i.product_id == product_id:
            item = i
            break

    if not item:
        return jsonify({"error": "Sản phẩm không có trong giỏ hàng"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify(stats_cart_db(cart))


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
    shipping_address = get_default_address_for_user(current_user)
    addresses = get_addresses_by_user(current_user)

    return render_template(
        "checkout.html",
        shipping_address=shipping_address,
        addresses=addresses
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
    except Exception:
        return jsonify({
            "success": False,
            "message": "Không thể cập nhật địa chỉ"
        }), 500


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
