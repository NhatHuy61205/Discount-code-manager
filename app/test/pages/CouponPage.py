from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage

class CouponPage(BasePage):
    URL = 'http://127.0.0.1:5000/coupon'
    SAVE_BTN = (By.CSS_SELECTOR, ".coupon-ticket-btn[type='submit']")
    MY_TAB_COUNT = (By.CSS_SELECTOR, ".coupon-tab-btn[data-coupon-tab='mine']")
    COUPON_OWNED = (By.CSS_SELECTOR, ".coupon-ticket-card-owned")

    def open_page(self):
        self.open(self.URL)

    def save_first_coupon(self):
        self.find(*self.SAVE_BTN).click()

    def get_my_coupon_count(self):
        return len(self.finds(*self.COUPON_OWNED))