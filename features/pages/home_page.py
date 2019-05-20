from selenium.webdriver.common.by import By

from features.pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, driver):
        base = "https://www.noel-wilson.co.uk"
        super(HomePage, self).__init__(driver, base, "")
