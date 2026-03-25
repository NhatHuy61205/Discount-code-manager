import hashlib
import re
import app.admin
from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required

from app import app
from app.dao import auth_user, get_user_by_phone, get_user_by_email, add_user, get_user_by_username
from app.models import Product, User, UserRole


@app.route("/")
def index():
    if current_user.is_authenticated and current_user.role == UserRole.ADMIN:
        return redirect(url_for("admin.index"))

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
            name = request.form.get("name", "").strip()
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            address = request.form.get("address", "").strip()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm", "")

            if not all([name, username, email, address, password, confirm]):
                raise ValueError("Vui lòng nhập đầy đủ thông tin")

            if len(password) < 8:
                raise ValueError("Mật khẩu phải tối thiểu 8 ký tự")

            if not re.search(r"[A-Za-z]", password):
                raise ValueError("Mật khẩu phải chứa chữ")

            if not re.search(r"\d", password):
                raise ValueError("Mật khẩu phải chứa số")

            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                raise ValueError("Mật khẩu phải chứa ký tự đặc biệt")

            if password != confirm:
                raise ValueError("Mật khẩu không khớp")

            if phone:
                if not re.fullmatch(r"\d{10}", phone):
                    raise ValueError("Số điện thoại phải đúng 10 chữ số")

            if get_user_by_username(username):
                raise ValueError("Tên đăng nhập đã tồn tại")

            if get_user_by_email(email):
                raise ValueError("Email đã tồn tại")


            if phone and get_user_by_phone(phone):
                raise ValueError("Số điện thoại đã được sử dụng")

            add_user(
                name=name,
                username=username,
                email=email,
                phone=phone,
                address=address,
                password=password
            )

            return redirect(url_for("login"))

        except Exception as e:
            err_msg = str(e)

    return render_template("register.html", error=err_msg)


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)