from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage


class CartPage(BasePage):
    URL = 'http://127.0.0.1:5000/cart'
    CART_ITEM_NAME = (By.CSS_SELECTOR, ".cart-item-row h6")

    def open_page(self):
        self.open(self.URL)

    def get_all_product_names(self):
        elements = self.finds(*self.CART_ITEM_NAME)
        return [e.text.strip() for e in elements]

    def is_product_in_cart(self, product_name):
        names = self.get_all_product_names()
        return product_name in names