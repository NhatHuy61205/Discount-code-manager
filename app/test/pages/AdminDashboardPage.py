from selenium.webdriver.common.by import By
from app.test.pages.BasePage import BasePage


class AdminDashboardPage(BasePage):

    ADMIN_NAME = (By.CSS_SELECTOR,'.admin-name')

    def get_admin_name(self):
        return self.find(*self.ADMIN_NAME).text