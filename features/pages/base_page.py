"""
Helpers to support Page patterns with selenium. This allows the construction of
tests which are less brittle. The Page Element abstracts the html allowing it
to change and be easily updated without needing to make too many changes to the
tests themselves.

http://selenium-python.readthedocs.org/page-objects.html

Oisin Mulvihll
2015-12-03

"""
import os
import re

from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

from lib.element import By
from lib.element import ElementSelector
from selenium.webdriver.support.expected_conditions import alert_is_present
from selenium.webdriver.support.ui import WebDriverWait

PAGE_TIMEOUT = int(os.environ.get('PAGE_TIMEOUT', 20))


class BasePage(object):
    """Base class for all page objects. See link below for page object pattern.
    All page elements that you wish to interact with should be defined here.
    You should inherit from this class to define your own page that represents
    a page in the browser.

    https://selenium-python.readthedocs.io/page-objects.html
    """

    # seconds
    TIMEOUT = PAGE_TIMEOUT

    def __init__(self, driver, base, path):
        """Create a page object

        :param driver: A selenium driver instance. This controls the connection
        :param base: The base url for the page e.g http://example.com
        """
        if not path.endswith("/") and not path.endswith(
            "(\#.*)?"
        ) and not re.match('^.*#[^/]', path):
            # If we are capturing for optional hash on end of URL e.g. (\#.*)?
            # then we don't need to explicitly handle the trailing slash case
            path += "/"
        self.base = base
        self.url = urljoin(self.base, path)
        self.driver = driver

    def make_screenshot(self, name):
        """Take a screenshot and save it to the filesystem

        :param name: Name of the file
        """
        out = self.driver.get_screenshot_as_png()
        with open('{}.png'.format(name), 'wb') as fd:
            fd.write(out)

    def go_to_page(self):
        """Navigate to the url represented by this page"""
        url = self.url
        self.driver.get(url)

    def go_to_link(self, link):
        """Navigate to provided link. This simulates cliking on a link

        :param link: Fully qualified url to go to.
        """
        self.driver.get(link)

    def go_to_rebased_link(self, link):
        """Navigate to link, rebased to be on the domain of this page. This is
        useful if you have a production url for example, but wish to go the
        local equivalent.

        :param link: Fully qualified url to  rebase and go to.
        """
        url = urlparse(link)
        netloc = urlparse(self.base).netloc
        self.go_to_link(urlunparse(url._replace(netloc=netloc)))

    def go_back(self):
        """Navigate to the previous page. Simulates clicking the browser back
        button."""
        self.driver.execute_script("window.history.go(-1)")

    def get_element(self, *names):
        """Get a (potentially nested inside section(s)) element off the page

        :param names: Sequence of element / section names

        :returns: A selenium element
        """
        element = self
        for name in names:
            element = getattr(element, name)

        return element

    def assert_on_page(self):
        """Assert that the current url is the one represented by this page
        object"""
        self.wait_until(
            lambda driver: re.match('^{}$'.format(
                self.url), driver.current_url),
            timeout=self.TIMEOUT
        )

    def click_on_text(self, text):
        """Click on the first element containing text on this page.

        :param text: Text to click on
        """
        ElementSelector.find(self.driver, By.CONTENT, text).click()

    def enter_on_text(self, text):
        """This is for when click_on_text fails to work due to
        “Element is not clickable at point” error, which is a bug with the
        chromium selenium driver.

        :param text: Text to 'click' on
        """
        ElementSelector.find(self.driver, By.CONTENT, text).send_keys('\n')

    def assert_text(self, text):
        """Assert that the text appears somewhere on this page.

        :param text: Text to look for on the page.
        """
        ElementSelector.find(self.driver, By.CONTENT, text)

    def scroll_into_view(self, element):
        """Scroll the page until the element is in the viewport.

        :param element: A selenium element.
        """
        ElementSelector.scroll_into_view(self.driver, element)

    def accept_alert(self):
        """Dismiss a alert dialog that appears in the browser"""
        self.wait_until(alert_is_present())
        alert = self.driver.switch_to_alert()
        alert.accept()

    def wait_until(self, condition, timeout=ElementSelector.TIMEOUT):
        """Wait unitl a condition has been fuliflled. This condition can be any
        function that you provide. The function will be continuously run until
        it returns True or the timeout elapses, at which point it will raise an
        exception.

        Commonly used functions can be found at the link below.

        https://selenium-python.readthedocs.io/waits.html

        :param condition: Any function
        :param timeout: Maximum lenght of time to wait before giving up
        (seconds)
        """
        WebDriverWait(self.driver, timeout).until(condition)

    def find_child_element(self, parent, by, selector):
        """Find a child element, waiting for it to appear

        :param parent: A selenium element.
        :param by: An instance of By.
        :param locator: A string to combine with `by` to locate the element'

        :returns: A selenium element
        """
        self.wait_until(lambda _: parent.find_element(by, selector))
        return parent.find_element(by, selector)
