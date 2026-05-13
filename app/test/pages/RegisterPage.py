from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage


class RegisterPage(BasePage):
    URL = 'http://127.0.0.1:5000/register'

    NAME = (By.NAME, 'name')
    USERNAME = (By.NAME, 'username')
    EMAIL = (By.NAME, 'email')
    PHONE = (By.NAME, 'phone')
    ADDRESS = (By.NAME, 'address')
    PASSWORD = (By.NAME, 'password')
    CONFIRM = (By.NAME, 'confirm')
    BTN_REGISTER = (By.CSS_SELECTOR, "form button[type='submit'], form button.btn-danger")

    def open_page(self):
        self.open(self.URL)

    def register(self, name, username, email, phone, address, password, confirm):
        self.typing(*self.NAME, name)
        self.typing(*self.USERNAME, username)
        self.typing(*self.EMAIL, email)
        self.typing(*self.PHONE, phone)
        self.typing(*self.ADDRESS, address)
        self.typing(*self.PASSWORD, password)
        self.typing(*self.CONFIRM, confirm)
        self.click(*self.BTN_REGISTER)