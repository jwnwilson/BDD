# -*- coding: utf-8 -*-
from lib.element import By
from lib.element import ElementSelector
from selenium.webdriver.support.select import Select


class Form(object):
    """This is a python descriptor that sets up a form when accessed from a
    page object.

    >>> class FooPage(BasePage):
    >>>     form = Form(
    >>>         TextInput('email')
    >>>     )
    >>>
    >>> foo_page = FooPage(driver, 'localhost', '/foo')
    >>> foo_page.form.complete('email', 'example@example.com')

    The above code will complete the email field with the content provided.
    """

    def __init__(self, *inputs):
        """Create a form.

        :param input: A list of form inputs
        """
        self.inputs = {input.alias: input for input in inputs}

    def __get__(self, parent, owner):
        """When an instance of this class is accessed from a parent class,
        the driver is copied from the parent.

        :param parent: The parent instance to which this instance belongs.
        :param owner: The type of the parent.

        :returns: itself
        """
        self.driver = parent.driver
        return self

    def complete(self, alias, value):
        input = self.inputs[alias]
        input.complete(self.driver, value)

    def verify(self, alias, value):
        input = self.inputs[alias]
        input.verify(self.driver, alias, value)


class FormInput(object):
    """Base class for form inputs"""

    def __init__(self, locator, alias=None, by=By.NAME):
        """See the below link for examples on how to locate elements
        https://selenium-python.readthedocs.io/api.html#locate-elements-by

        :param locator: A string to combine with `by` to locate the element'
        :param alias: An alternate name for the input, defaults to locator
        :param by: An instance of By.
        """
        self.by = by
        self.locator = locator
        self.alias = alias or locator

    def _find_element(self, driver, multiple=False, by=None):
        by = by or self.by
        return ElementSelector.find(
            driver, by, self.locator, multiple=multiple
        )

    def complete(self, driver, value):
        """Complete the input with the specified value

        :param driver: A selenium driver instance. This controls the connection
        to the browser.
        :param value: The value to send to the input.
        """
        pass

    def verify(self, driver, alias, value):
        """Verify that the input has the expected value

        :param driver: A selenium driver instance. This controls the connection
        to the browser.
        :param alias: The alternate name of the input, used for debugging.
        :param value: The value to send to the input.
        """
        element = self._find_element(driver)
        observed_value = element.get_attribute('value')
        if (not observed_value == value):
            print((
                "Expected %s to be %s but got %s" %
                (alias, value, observed_value)
            ))
            raise Exception


class TextInput(FormInput):
    """An input that expects text to be sent to it"""

    def __init__(self, locator, alias=None, by=By.NAME, clear=True):
        super(TextInput, self).__init__(locator, alias, by)
        self.clear = clear

    def complete(self, driver, text):
        element = self._find_element(driver)
        ElementSelector.scroll_into_view(driver, element)
        if self.clear:
            element.clear()
        element.send_keys(text)


class CheckableGroupInput(FormInput):
    """An input of a group of checkable elements. E.g. a group of checkboxes or
    radio buttons. The locator should select all the inputs in this group."""

    def complete(self, driver, label_content):
        inputs = self._find_element(driver, multiple=True)

        for input in inputs:
            id = input.get_attribute("id").replace(
                '.', '\.'
            )  # IDs with '.' need to be escaped
            label = ElementSelector.find(
                driver, By.CSS_SELECTOR, "label[for={}]".format(id)
            )
            if label.text == label_content and not input.is_selected():
                ElementSelector.scroll_into_view(driver, input)
                label.click()
                break


class RadioGroupInput(CheckableGroupInput):
    pass


class CheckboxGroupInput(CheckableGroupInput):
    pass


class CheckboxTupleGroupInput(CheckableGroupInput):
    pass


class CheckboxDatedGroupInput(CheckableGroupInput):
    pass


class RadioInput(FormInput):
    """An individual radio button"""

    def complete(self, driver, _):
        element = self._find_element(driver)
        ElementSelector.scroll_into_view(driver, element)
        if not element.is_selected():
            element.click()


class CheckboxInput(FormInput):
    """An individual checkbox"""

    def complete(self, driver, checked):
        """Check or uncheck the input.

        :param driver: A selenium driver instance. This controls the connection
        to the browser.
        :param checked: Either the string 'checked' or 'unchecked'
        """
        element = self._find_element(driver)
        ElementSelector.scroll_into_view(driver, element)
        if element.is_selected() ^ (checked == 'checked'):
            ElementSelector.scroll_into_view(driver, element)
            element.click()

    def verify(self, driver, alias, value):
        """Verify that the input is checked or unchecked.

        :param driver: A selenium driver instance. This controls the connection
        to the browser.
        :param alias: The alternate name of the input, used for debugging.
        :param checked: Either the string 'checked' or 'unchecked'
        """
        element = self._find_element(driver)
        if (value == 'checked' and not element.is_selected()):
            print((
                "Expected %s to be checked but element is not selected: %s" %
                (alias, value)
            ))
            raise Exception
        if (value == 'unchecked' and element.is_selected()):
            print(("Expected %s to be unchecked but got %s" % (alias, value)))
            raise Exception


class MultiSelectInput(FormInput):
    """A multi select input i.e. a dropdown where more than one item may be
    selected"""

    def complete(self, driver, label_content):
        """Toggle the selection of the option based on the visible text of the
        label. This method opens the dropdown, toggles the item and then closes
        the dropdown.

        :param driver: A selenium driver instance. This controls the connection
        to the browser.
        :param label_content: The text that is displayed to the user on that
        option
        """
        dropdown = self._find_element(driver)
        dropdown.click()
        labels = dropdown.find_elements(By.CSS_SELECTOR, 'label')
        for label in labels:
            if label.text == label_content:
                ElementSelector.scroll_into_view(driver, label)
                label.click()
                break
        dropdown.click()


class DropdownItem(FormInput):
    """A single select input i.e. a dropdown where one item may be
    selected"""

    def complete(self, driver, label_content):
        """Selection an the option based on the visible text of the
        label.

        :param driver: A selenium driver instance. This controls the connection
        to the browser.
        :param label_content: The text that is displayed to the user on that
        option
        """
        inputs = self._find_element(driver, multiple=True)

        for input in inputs:
            label = ElementSelector.find(driver, By.CONTENT, label_content)
            if label.text == label_content:
                ElementSelector.scroll_into_view(driver, input)
                label.click()
                break


class SelectInput(FormInput):
    def complete(self, driver, text):
        element = self._find_element(driver)
        ElementSelector.scroll_into_view(driver, element)
        select = Select(element)
        select.select_by_visible_text(text)

    def verify(self, driver, alias, value):
        element = self._find_element(driver)
        select = Select(element)
        observed_value = select.first_selected_option.text
        if (not observed_value == value):
            print((
                "Expected %s to be %s but got %s" %
                (alias, value, observed_value)
            ))
            raise Exception


class DateInput(FormInput):
    """A three-part date input"""

    def complete(self, driver, info):
        """Find and complete a date input

        :param driver: A selenium driver instance. This controls the connection
        to the browser.
        :param info: A specified of the form 'name:dd/mm/yyyy', where the name
        is the name attribute on the input.
        """
        intToMonth = {
            '1': 'Jan',
            '2': 'Feb',
            '3': 'Mar',
            '4': 'Apr',
            '5': 'May',
            '6': 'Jun',
            '7': 'Jul',
            '8': 'Aug',
            '9': 'Sep',
            '10': 'Oct',
            '11': 'Nov',
            '12': 'Dec'
        }

        name, date = info.split(':', 1)
        day, month, year = date.split('/', 2)
        day = day.lstrip('0')
        month = intToMonth[month.lstrip('0')]

        day_selector = SelectInput(name + '-day')
        month_selector = SelectInput(name + '-month')
        year_selector = SelectInput(name + '-year')

        day_selector.complete(driver, day)
        month_selector.complete(driver, month)
        year_selector.complete(driver, year)


class Button(FormInput):
    """A simple button within a form."""

    def complete(self, driver, _):
        element = self._find_element(driver)
        element.click()
