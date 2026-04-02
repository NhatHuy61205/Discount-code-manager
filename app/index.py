import app.admin
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required

from app import app
from app.dao import (
    auth_user, get_active_products, register_user,
    get_best_coupon_for_product, get_product_by_id,
    get_cart_items_by_user, get_suggested_products
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

    return render_template(
        "cart.html",
        cart_items=cart_items,
        suggested_products=suggested_products
    )

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)