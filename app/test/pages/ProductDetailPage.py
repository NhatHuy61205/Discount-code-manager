from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage

class ProductDetailPage(BasePage):
    NAME = (By.CSS_SELECTOR, 'h3.fw-bold')
    PRICE = (By.CSS_SELECTOR, 'h4.text-danger')
    QTY_INPUT = (By.ID, 'qty')
    ADD_TO_CART_BTN = (By.ID, 'add-to-cart-btn')
    SUCCESS_TOAST = (By.ID, 'cart-success-toast')

    def get_product_name(self):
        return self.find(*self.NAME).text.strip()

    def click_add_to_cart(self):
        self.click(*self.ADD_TO_CART_BTN)

    def add_to_cart(self):
        self.click_add_to_cart()