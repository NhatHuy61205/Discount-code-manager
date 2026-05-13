from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage

class CouponModalPage(BasePage):
    COUPONS = (By.CSS_SELECTOR, ".cart-coupon-item")
    CONFIRM_BTN = (By.ID, "sharedCouponModalConfirm")

    def select_first_coupon(self):
        self.finds(*self.COUPONS)[0].click()

    def confirm(self):
        self.click(*self.CONFIRM_BTN)