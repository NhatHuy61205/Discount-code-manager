from flask import Flask, render_template

from app import app
from app.models import Product


@app.route("/")
def index():
    hero_banners = [f"pics/pics_sale{i}.jpg" for i in range(1, 5)]

    products = Product.query.filter_by(active=True).all()

    return render_template(
        "index.html",
        hero_banners=hero_banners,
        products=products
    )
if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)