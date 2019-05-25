import urllib.parse

from behave import Then
from behave import When
from lib.element import By
from lib.element import ElementSelector
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


@When('I go to the {page} page')
def go_to(context, page):
    context.get_page(page).go_to_page()


@When('I search on {page} page with {query} {parameter}')
def go_to_and_search(context, page, query, parameter):
    pageUrl = context.get_page(page).url
    url = pageUrl + '?' + urllib.parse.urlencode({parameter: query})
    context.get_page(page).go_to_link(url)


@When('I am redirected to the {page} page')
def redirect_to(context, page):
    context.get_page(page).go_to_page()


@When('I click on "{text}" on the {page} page')
def click_on_text(context, text, page):
    context.get_page(page).click_on_text(text)


@When('I hit enter on "{text}" on the {page} page')
def enter_on_text(context, text, page):
    context.get_page(page).enter_on_text(text)


@Then('I see "{text}" on the {page} page')
def assert_text(context, text, page):
    context.get_page(page).click_on_text(text)


@Then('I see "{message}" contained on the {page} page')
def assert_carer_onboarding_status_text(context, message, page):
    driver = context.get_page(page).driver
    locator = '(//*[contains(normalize-space(.), "{}")])'.format(message)
    try:
        WebDriverWait(
            driver,
            ElementSelector.TIMEOUT,
        ).until(lambda _: driver.find_elements(By.XPATH, locator))
    except TimeoutException:
        raise TimeoutException(
            msg=(
                "ElementSelector not found. "
                "Locator: '%s'. Find method: 'XPATH'" % (locator)
            )
        )


@When('I click the nav item "{text}" on the app {page} page')
@When('I click on the nav item "{text}" on the app {page} page')
def click_on_nav(context, text, page):
    context.get_page('app', page).click_primary_nav_item(text)


@Then('I am on the {application} {page} page')
def assert_page(context, application, page):
    context.get_page(application, page).assert_on_page()


@When('I accept the alert on the {application} {page} page')
def accept_alert(context, application, page):
    context.get_page(application, page).accept_alert()
