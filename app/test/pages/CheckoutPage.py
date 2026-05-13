from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage

class CheckoutPage(BasePage):
    URL = "http://127.0.0.1:5000/checkout"
    ADDRESS = (By.ID, "checkoutUser")
    PLACE_ORDER_BTN = (By.CLASS_NAME, "checkout-place-order-btn")
    SUCCESS_TOAST = (By.ID, "order-success-toast")

    def open_page(self):
        self.open(self.URL)

    def get_shipping_address(self):
        return self.find(*self.ADDRESS).text.strip()

    def place_order(self):
        self.click(*self.PLACE_ORDER_BTN)

    def is_success_message_displayed(self):
        return self.find(*self.SUCCESS_TOAST).is_displayed()