from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage


class AdminCouponPage(BasePage):
    URL = "http://127.0.0.1:5000/admin/coupon/"

    CREATE_BTN = (By.CSS_SELECTOR, "a.btn.btn-danger, a[href*='create']")

    NAME = (By.NAME, "name")
    CODE = (By.NAME, "code")
    DISCOUNT_FIXED = (By.CSS_SELECTOR, "input[name='discount_kind'][value='fixed']")
    DISCOUNT_VALUE = (By.NAME, "discount_value")
    MIN_ORDER = (By.NAME, "min_order_value")
    QUANTITY = (By.NAME, "quantity")

    SUBMIT = (By.CSS_SELECTOR, "button[type='submit'], .coupon-submit-btn")

    COUPON_CODE_LIST = (By.CSS_SELECTOR, ".coupon-table .fw-bold")

    def open_page(self):
        self.open(self.URL)

    def click_create_coupon(self):
        self.click(*self.CREATE_BTN)

    def set_date(self, element_id, value):
        self.driver.execute_script("""
            const el = document.getElementById(arguments[0]);
            const fp = el._flatpickr;

            fp.setDate(arguments[1], true);
        """, element_id, value)

    def create_coupon(self, name, code, discount_value, min_order, quantity, start_date, end_date):
        self.typing(*self.NAME, name)
        self.typing(*self.CODE, code)

        self.click(*self.DISCOUNT_FIXED)

        self.typing(*self.DISCOUNT_VALUE, discount_value)
        self.typing(*self.MIN_ORDER, min_order)
        self.typing(*self.QUANTITY, quantity)

        self.set_date("start_date", start_date)
        self.set_date("end_date", end_date)

        self.click(*self.SUBMIT)

    def is_coupon_exists(self, code):
        elements = self.driver.find_elements(*self.COUPON_CODE_LIST)

        for element in elements:
            if code == element.text.strip():
                return True

        return False

    def get_success_alert(self):
        return self.driver.find_element(By.CSS_SELECTOR, ".alert.alert-success")