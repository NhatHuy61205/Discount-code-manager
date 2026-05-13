import time
import pytest
from selenium.webdriver.common.by import By
from app.test.pages.LoginPage import LoginPage
from app.test.pages.RegisterPage import RegisterPage
from app.test.pages.HomePage import HomePage
from app.test.pages.ProductDetailPage import ProductDetailPage
from app.test.pages.AdminDashboardPage import AdminDashboardPage
from app.test.pages.CartPage import CartPage
from app.test.test_base import driver


def test_login_admin_success(driver):
    login = LoginPage(driver=driver)
    admin = AdminDashboardPage(driver)
    login.open_page()

    login.login('admin', 'admin123')

    time.sleep(1)

    assert '/admin/' in driver.current_url
    assert 'Admin' in admin.get_admin_name()


def test_login_user_success(driver):
    login = LoginPage(driver=driver)
    home = HomePage(driver)
    login.open_page()

    login.login('user1', '123456')

    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/'
    assert 'User 1' in home.get_user_name()

def test_register_success(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register('ABCDEFGH', 'abcdefGH', 'AbcdefGH@gmail.com', '0213456879', 'TPHCM', 'Abc@12345', 'Abc@12345')

    time.sleep(3)

    login = LoginPage(driver=driver)
    login.login('abcdefgh', 'Abc@12345')

    time.sleep(3)

    home = HomePage(driver)
    assert 'ABCDEFGH' in home.get_user_name()


def test_search_products(driver):
    home = HomePage(driver=driver)
    home.open_page()

    kw = 'Cardigan'
    home.search(kw)
    time.sleep(1)

    results = driver.find_elements(By.CSS_SELECTOR, 'section#products .card-title')

    assert len(results) > 0
    assert all(kw.lower() in r.text.lower() for r in results)


def test_view_product_detail_success(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login('user1', '123456')

    home = HomePage(driver)
    home.open_page()

    home.click_view_detail()

    detail = ProductDetailPage(driver)
    time.sleep(3)

    assert '/product/' in driver.current_url

def test_add_to_cart(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login('user1', '123456')

    home = HomePage(driver)
    home.click_view_detail()
    time.sleep(3)

    detail = ProductDetailPage(driver)
    product_name = detail.get_product_name()
    detail.add_to_cart()
    time.sleep(3)

    cart = CartPage(driver)
    cart.open_page()
    time.sleep(3)

    assert cart.is_product_in_cart(product_name) is True