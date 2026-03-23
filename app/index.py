from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required

from app import app
from app.dao import auth_user
from app.models import Product, User


@app.route("/")
def index():
    hero_banners = [f"pics/pics_sale{i}.jpg" for i in range(1, 5)]

    products = Product.query.filter_by(active=True).all()

    return render_template(
        "index.html",
        hero_banners=hero_banners,
        products=products
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    err_msg = None

    if current_user.is_authenticated:
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


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)