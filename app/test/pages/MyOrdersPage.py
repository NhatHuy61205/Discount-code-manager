from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage


class MyOrdersPage(BasePage):
    URL = 'http://127.0.0.1:5000/my-orders'

    ORDER_ITEMS = (By.CSS_SELECTOR, ".my-order-item__name")

    def open_page(self):
        self.open(self.URL)

    def is_product_in_orders(self, product_name):
        orders = self.finds(*self.ORDER_ITEMS)

        for order in orders:
            if product_name in order.text:
                return True

        return False