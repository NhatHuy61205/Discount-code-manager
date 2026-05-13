import pytest
from flask import Flask
from app import db
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    db.init_app(app)
    return app


@pytest.fixture
def test_app():
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()

@pytest.fixture
def driver():
    service = Service(executable_path='.venv/chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()