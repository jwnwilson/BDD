"""
This file is the entry point for behave. This file is evaluated before any
scenarios are run.

There are also lifecycle hooks defined in here that run at the specified time.

https://behave.readthedocs.io/en/latest/tutorial.html#environmental-controls
"""
import logging
import os
import re
import subprocess

import requests

from behave import *  # noqa F401
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from features.pages.home_page import HomePage


def before_all(context):
    context.logger = __configure_logger()


def before_scenario(context, scenario):
    """Truncate and load fixture data and set up connection to selenium and
    page objects. Make a new driver each time to get a fresh session"""

    context.driver = __configure_selenium_driver(context.logger)

    context.home = HomePage(context.driver)
    context.get_page = lambda page: getattr(context, page)  # noqa: E501
    context.driver.set_window_size(1280, 800)
    if int(os.getenv('MOBILE_BROWSER', 0)):
        context.driver.set_window_size(412, 732)


def before_step(context, step):
    pass


def after_step(context, step):
    if int(os.getenv('SCREENSHOTS', 0)):
        __take_screenshot(
            context.logger, context.driver,
            '{}_{}'.format(re.sub(r'/', '_', step.filename), step.line)
        )


def after_scenario(context, scenario):
    """Take a screenshot if the scenario failed."""

    if scenario.status != 'passed':
        __take_screenshot(context.logger, context.driver, scenario.name)

        if int(os.getenv('PDB_ON_FAILURE', 0)):
            context.logger.error(
                "Opening debug console on scenario: {}".format(scenario.name)
            )
            import ipdb
            ipdb.set_trace()  # noqa

    context.driver.close()
    # context.driver.delete_all_cookies()
    # context.driver.execute_script("window.localStorage.clear();")


def after_all(context):
    pass


def __configure_logger():
    logger = logging.getLogger('integration')
    hdlr = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger


def __configure_selenium_driver(logger):
    """Setup the selenium driver in one of the following modes:
            local: default - local chrome driver
            remote: remote selenium server
            saucelabs: saucelabs server

        :returns: an selenium driver instance
    """
    SELENIUM_MODE = os.getenv('SELENIUM_MODE', 'local')
    SELENIUM_BASE_URI = os.getenv('SELENIUM_BASE_URI')

    logger.info(
        "Using selenium mode '{}' with base uri '{}'".format(
            SELENIUM_MODE, SELENIUM_BASE_URI
        )
    )

    if SELENIUM_MODE == "local":
        return webdriver.Chrome()
    elif SELENIUM_MODE == "remote":
        return webdriver.Remote(
            command_executor=SELENIUM_BASE_URI,
            desired_capabilities=DesiredCapabilities.CHROME
        )


def __take_screenshot(logger, driver, name):
    filename = "screenshots/{}.png".format(name.lower().replace(' ', '_'))
    screenshot = driver.save_screenshot(filename)
    logger.info(
        "Took screenshot of failing scenario to '{}'".format(filename)
    )
