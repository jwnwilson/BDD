# -*- coding: utf-8 -*-
from lib.element import ElementSelector


class SectionSelector(object):
    """This is a python descriptor that defines a section of the page. Any
    child elements are scoped to be within this section. Sections can be nested
    to further limit the scope of child elements.

    >>> class FooPage(BasePage):
    >>>     section = SectionSelector(By.CSS_SELECTOR, '#button-bar',
    >>>         button=ElementSelector(By.CSS_SELECTOR, 'button')
    >>>         subsection=SectionSelector(By.CSS_SELECTOR, '#errors',
    >>>             errors=ElementSelector(
    >>>                 By.CSS_SELECTOR, '.error', multiple=True
    >>>             )
    >>>         )
    >>>     )
    >>>
    >>> foo_page = FooPage(driver, 'localhost', '/foo')
    >>> foo_page.section.button
    >>> foo_page.section.subsection.errors

    When the button, or errors are accessed, as above, they are resolved into
    selenium elements.

    You can also access the element of the section itself, by using

    >>> foo_page.section.element
    """

    def __init__(self, by, locator, **children):
        """Create a scope. This can be set up before the page has
        loaded. The scope is only resolved when the attribute is accessed.

        See the below link for examples on how to locate elements
        https://selenium-python.readthedocs.io/api.html#locate-elements-by

        :param by: An instance of By.
        :param locator: A string to combine with `by` to locate the scope
        :param children: A dict of child element selectors or scopes.
        """
        self.by = by
        self.locator = locator
        self.children = children

    def __get__(self, parent, owner):
        """When an instance of this class is accessed from a parent class,
        it is resolved into a section instance.

        :param parent: The parent instance to which this instance belongs.
        :param owner: The type of the parent.

        :returns: An instance of Section
        """

        class Section(object):
            driver = parent.driver
            element = ElementSelector.find(
                driver,
                self.by,
                self.locator,
                scope=getattr(parent, 'element', None)
            )

        for name, child in list(self.children.items()):
            setattr(Section, name, child)

        return Section()
