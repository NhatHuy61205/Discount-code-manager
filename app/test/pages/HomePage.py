from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage


class HomePage(BasePage):
    URL = 'http://127.0.0.1:5000/'
    USER_NAME = (By.CSS_SELECTOR, '.header-user-trigger')
    SEARCH_INPUT = (By.NAME, 'keyword')
    SEARCH_BTN = (By.CSS_SELECTOR, '#mainNavbar form button[type="submit"]')

    PRODUCT_TITLE = (
        By.CSS_SELECTOR,
        '.product-card .card-title'
    )
    VIEW_DETAIL_BTN = (By.CSS_SELECTOR, '.product-card .btn-outline-danger')

    def open_page(self):
        self.open(self.URL)

    def search(self, keyword):
        self.typing(*self.SEARCH_INPUT, keyword)
        self.click(*self.SEARCH_BTN)

    def get_first_product_name(self):
        return self.find(*self.PRODUCT_TITLE).text

    def click_view_detail(self):
        self.click(*self.VIEW_DETAIL_BTN)

    def get_user_name(self):
        return self.find(*self.USER_NAME).text