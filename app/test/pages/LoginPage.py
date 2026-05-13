from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage


class LoginPage(BasePage):
    URL = 'http://127.0.0.1:5000/login'
    USERNAME = (By.NAME, 'username')
    PASSWORD = (By.NAME, 'password')
    BTN = (By.CSS_SELECTOR, 'div.d-grid > button.btn.btn-danger.rounded-pill')

    def open_page(self, url=URL):
        self.open(url)

    def login(self, username, password):
        self.typing(*self.USERNAME, username)
        self.typing(*self.PASSWORD, password)
        self.click(*self.BTN)