from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CartPage(BasePage):
    URL = 'http://127.0.0.1:5000/cart'
    CART_ITEM_NAME = (By.CSS_SELECTOR, ".cart-item-row h6")

    QTY_INCREASE = (By.CSS_SELECTOR, ".qty-btn.qty-increase")
    QTY_DECREASE = (By.CSS_SELECTOR, ".qty-btn.qty-decrease")
    QTY_INPUT = (By.CSS_SELECTOR, ".qty-input")
    DELETE_BUTTON = (By.CSS_SELECTOR, ".cart-delete-link")

    CHECKBOX = (By.CSS_SELECTOR, ".cart-item-checkbox")
    OPEN_COUPON_BTN = (By.ID, "openCartCouponModal")
    GRAND_TOTAL = (By.ID, "cartGrandTotal")

    def open_page(self):
        self.open(self.URL)

    def get_all_product_names(self):
        elements = self.finds(*self.CART_ITEM_NAME)
        return [e.text.strip() for e in elements]

    def is_product_in_cart(self, product_name):
        elements = self.finds(*self.CART_ITEM_NAME)

        for element in elements:
            if product_name == element.text.strip():
                return True

        return False

    def increase_quantity(self, times=1):
        for _ in range(times):
            self.click(*self.QTY_INCREASE)
            self.driver.implicitly_wait(1)

    def decrease_quantity(self, times=1):
        for _ in range(times):
            self.click(*self.QTY_DECREASE)
            self.driver.implicitly_wait(1)

    def get_quantity(self):
        value = self.find(*self.QTY_INPUT).get_attribute("value")
        return int(value)

    def delete_first_product(self):
        self.find(*self.DELETE_BUTTON).click()
        self.find(By.ID, "cartDeleteModalConfirm").click()

        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".cart-item-row"))
        )

    def select_first_item(self):
        self.finds(*self.CHECKBOX)[0].click()

    def open_coupon_modal(self):
        self.click(*self.OPEN_COUPON_BTN)

    def get_total(self):
        text = self.find(*self.GRAND_TOTAL).text
        return int(text.replace(".", "").replace("đ", ""))

    def click_checkout(self):
        self.click(By.ID, "cartBuyBtn")