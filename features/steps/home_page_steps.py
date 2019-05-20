from behave import given
from behave import step
from behave import when
import re


@given('I am redirected on home page')
def navigate_to_home_page(context):
    assert context.browser.current_url == "{}".format(
        context.home_page.project_url)


@step('On home page I want to see {text}')
@step('On searching page I want to see {text}')
def check_element_on_home_page(context, text):
    context.home.assert_text(text)