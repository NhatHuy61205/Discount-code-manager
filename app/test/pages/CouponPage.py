from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage

class CouponPage(BasePage):
    URL = 'http://127.0.0.1:5000/coupon'
    SAVE_BTN = (By.CSS_SELECTOR, ".coupon-ticket-btn[type='submit']")
    MY_TAB_COUNT = (By.CSS_SELECTOR, ".coupon-tab-btn[data-coupon-tab='mine']")

    def open_page(self):
        self.open(self.URL)

    def save_all_coupons(self):
        buttons = self.finds(*self.SAVE_BTN)

        for btn in buttons:
            try:
                btn.click()
                self.driver.implicitly_wait(1)
            except:
                pass