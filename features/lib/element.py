# -*- coding: utf-8 -*-
import os

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

By.CONTENT = 'content'


class ElementSelector(object):
    """This is a python descriptor that selects a selenium element on
    the page when accessed from a parent object.

    This allows you to set up selectors that are only run when you access them.

    >>> class FooPage(BasePage):
    >>>     button = ElementSelector(By.CSS_SELECTOR, 'button')
    >>>
    >>> foo_page = FooPage(driver, 'localhost', '/foo')
    >>> foo_page.button

    When the button is accessed, as above, it is resolved into a selenium
    element.

    See the below link for available methods on selenium elements.
    https://seleniumhq.github.io/selenium/docs/api/py/webdriver_remote/selenium.webdriver.remote.webelement.html
    """
    TIMEOUT = int(os.environ.get('PAGE_ELEMENT_TIMEOUT', 5))

    def __init__(self, by, locator, multiple=False):
        """Create an element selector. This can be set up before the page has
        loaded. The element is only resolved when the attribute is accessed.

        See the below link for examples on how to locate elements
        https://selenium-python.readthedocs.io/api.html#locate-elements-by

        :param by: An instance of By.
        :param locator: A string to combine with `by` to locate the element'
        :param multiple: Boolean, if true returns a list of items rather than
        the first item.
        """
        self.by = by
        self.locator = locator
        self.multiple = multiple

    def __get__(self, parent, owner):
        """When an instance of this class is accessed from a parent class,
        it is resolved into the selenium element.

        :param parent: The parent instance to which this instance belongs.
        :param owner: The type of the parent.

        :returns: A selenium element

        See the below link for available methods on selenium elements.
        https://seleniumhq.github.io/selenium/docs/api/py/webdriver_remote/selenium.webdriver.remote.webelement.html
        """
        return ElementSelector.find(
            parent.driver,
            self.by,
            self.locator,
            multiple=self.multiple,
            scope=getattr(parent, 'element', None)
        )

    @classmethod
    def find(cls, driver, by, locator, multiple=False, scope=None):
        """Resolve this selector into the element on the page.

        :param driver: A selenium driver instance. This controls the connection
        to the browser.
        :param by: An instance of By.
        :param locator: A string to combine with `by` to locate the element'
        :param multiple: Boolean, if true returns a list of items rather than
        the first item.
        :param scope: Containing element. If provided, the selector will only
        return elements that are children of this. If omitted, the scope is the
        entire page.

        :returns: A selenium element

        See the below link for available methods on selenium elements.
        https://seleniumhq.github.io/selenium/docs/api/py/webdriver_remote/selenium.webdriver.remote.webelement.html
        """
        if not scope:
            scope = driver

        try:
            if by == By.CONTENT:
                by = By.XPATH
                locator = '//*[normalize-space() = "{}"]/text()/..'.format(
                    locator
                )
                WebDriverWait(
                    driver,
                    cls.TIMEOUT,
                ).until(lambda _: scope.find_elements(by, locator))
                elements = scope.find_elements(by, locator)
                if multiple:
                    return elements
                return elements[0]

            else:
                if multiple:
                    finder = scope.find_elements
                else:
                    finder = scope.find_element

                WebDriverWait(
                    driver,
                    cls.TIMEOUT,
                ).until(lambda _: finder(by, locator))
                return finder(by, locator)
        except TimeoutException:
            raise TimeoutException(
                msg=(
                    "Element not found. "
                    "Locator: '%s'. Find method: '%s'" % (locator, by)
                )
            )

    @classmethod
    def scroll_into_view(self, driver, element):
        """Scroll the page until the element is in the viewport.

        :param driver: A selenium driver instance. This controls the connection
        to the browser.
        :param element: A selenium element.
        """
        driver.execute_script(
            "arguments[0].scrollIntoView({ block: 'center' })", element
        )
