"""Test WebSupervisor in North Europe and Australia.

Open WSV - check browser title
Login - check logged user name
Go to units - count units
"""
import json
import logging
import os
import time
import unittest
from datetime import datetime

import pymsteams
from parameterized import parameterized_class
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

#
# Define global variables and constants
#

xpath_username = '//*[@id="microsite-login-name"]'
xpath_password = '//*[@id="microsite-login-password"]'
xpath_login = '//*[@id="intro"]/div[1]/div/div[1]/div/form/div[3]/input'
xpath_login_id = (
    "/html/body/div[4]/div/div[1]/div[1]/div/header/div[2]/ul/li[1]/span[1]"
)
xpath_units = '//*[@id="main-menu-nav"]/ul/li[2]/a'

test_enabled = True
send_to_teams = False

#
# Logger
#

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


#
# Helpers
#

def format_message(msg):
    """Format the message."""

    test = msg[0]._testMethodName
    error = msg[1]
    assertion = error[error.find("AssertionError") + 15:]

    return test + assertion[assertion.find(":") + 1:]


# pylint: disable=no-member


@parameterized_class(
    # json.load(os.environ["CONFIG"])
    json.load(open('config.local.json'))
)
class TestWSV(unittest.TestCase):
    """WebSupervisor tests."""

    def setUp(self):
        """Test fixture - open the browser."""
        logger.info("\n" + "-" * 32 + "\nSetting test up for %s\n" + "-" * 32, self.location)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.maximize_window()
        self.browser.implicitly_wait(60)

    def tearDown(self):
        """Close the browser window."""
        logger.info("Tearing down test for %s", self.url)
        self.browser.quit()

    def assertIn(self, member, container, msg=None):
        """Redefine method to include datacenter name."""
        if msg is not None:
            super().assertIn(member, container, f"{self.location}: {msg}")
        else:
            super().assertIn(member, container)

    def assertIsNotNone(self, expr, msg=None):
        """Redefine method to include datacenter name."""
        if msg is not None:
            super().assertIsNotNone(expr, f"{self.location}: {msg}")
        else:
            super().assertIsNotNone(expr)

    def assertTrue(self, expr, msg=None):
        """Redefine method to include datacenter name."""
        if msg is not None:
            super().assertTrue(expr, f"{self.location}: {msg}")
        else:
            super().assertTrue(expr)

    def wait_find_element_by_xpath(self, maxTimeOut, locator):
        """In case the element got destroyed, wait for it to be recreated."""
        element = None
        try:
            WebDriverWait(
                self.browser,
                maxTimeOut,
                ignored_exceptions=[StaleElementReferenceException],
            ).until(EC.presence_of_element_located((By.XPATH, locator)))
            element = self.browser.find_element_by_xpath(locator)
        except Exception:
            raise NoSuchElementException(
                "Exception occurred during object identification."
            )
        return element

    def wait_find_elements_by_class_name(self, maxTimeOut, locator):
        """In case the element got destroyed, wait for it to be recreated."""
        try:
            WebDriverWait(
                self.browser,
                maxTimeOut,
                ignored_exceptions=[StaleElementReferenceException],
            ).until(EC.presence_of_all_elements_located((By.CLASS_NAME, locator)))
            elements = self.browser.find_elements_by_class_name(locator)
        except Exception:
            raise NoSuchElementException(
                "Exception occurred during object identification."
            )
        return elements

    def test_WSV(self):
        """Main test case."""

        # Open WebSupervisor, check page title
        self.browser.get(self.url)
        logger.info("Testing website title")
        logger.info("Title: %s", self.browser.title)

        self.assertIsNotNone(self.browser.title, "Can't find the webpage title. Is WebSupervisor down?")
        self.assertIn(
            "WebSupervisor",
            self.browser.title,
            "The webpage title does not match. "
            f'Expected "WebSupervisor", found "{self.browser.title}"',
        )

        try:
            username = self.wait_find_element_by_xpath(60, xpath_username)
            password = self.wait_find_element_by_xpath(60, xpath_password)
            login = self.wait_find_element_by_xpath(60, xpath_login)
        except NoSuchElementException:
            login = None

        self.assertTrue(
            login is not None and username is not None and login is not None,
            "The Login fields not found!",
        )

        # Login, check user name
        username.clear()
        username.send_keys(self.user_name)
        password.clear()
        password.send_keys(self.user_password)
        login.click()
        logger.info("Testing logged user name")
        try:
            login_id = self.wait_find_element_by_xpath(60, xpath_login_id).text
        except (NoSuchElementException, AttributeError):
            login_id = None
        logger.info("Logged user: %s", login_id)
        self.assertIsNotNone(login_id, "Can't find username. Login not working?")
        self.assertIn(
            self.display_name,
            login_id,
            f'The username does not match! Expected "{self.display_name}",'
            f' found "{login_id}"',
        )

        # Go to Units section, count the number of units
        try:
            units_button = self.wait_find_element_by_xpath(60, xpath_units)
        except NoSuchElementException:
            units_button = None
        self.assertIsNotNone(units_button, 'The "units" button not found')
        units_button.click()
        try:
            table = self.wait_find_elements_by_class_name(60, "main-table")
        except NoSuchElementException:
            table = None
        self.assertIsNotNone(table, "Unit table not found")
        table_rows = table[0].find_elements_by_tag_name("tr")
        units = []
        logger.info("Testing list of units")
        for row in table_rows:
            unit = row.find_elements_by_tag_name("td")[2]
            if unit.text != "":
                units.append(unit.text)
                logger.info("Unit: %s", unit.text)
        logger.info("Found %d units", len(units))
        self.assertTrue(
            len(units) >= self.unit_count,
            f"Number of units does not match. Found {len(units)}, "
            f"expected {self.unit_count}",
        )


def send_msteams_message(state, timestamp, message="", dry_run=True):
    """Post error message to Teams."""
    # if platform.system() == "Windows":
    if not send_to_teams:
        if state:
            print("Automated WSV alert canceled (beta)")
            print(f"{timestamp}: WSV is running normaly.")
        else:
            print("Automated WSV Alert (beta)")
            print(f"{timestamp}: The automated WSV checking script has failed.{message}")
    else:
        my_teams_message = pymsteams.connectorcard(os.environ.get['TEAMS_WEBHOOK'])
        if state:
            my_teams_message.title("Automated WSV alert canceled (beta)")
            my_teams_message.text(f"{timestamp}: WSV is running normaly.")
        else:
            my_teams_message.title("Automated WSV Alert (beta)")
            my_teams_message.text(
                f"{timestamp}: The automated WSV checking script has failed.{message}"
            )
            if "North_Europe" in message:
                my_teams_message.addLinkButton("Check WSV in North Europe!", "https://www.websupervisor.net")
            if "Australia" in message:
                my_teams_message.addLinkButton("Check WSV in Australia!", "https://aus.websupervisor.net")
        my_teams_message.send()


if __name__ == "__main__":
    logger.info("Starting WSV testing")

    # Define global variable
    status = {"status": None, "last_change": None, "message": ""}

    while True:
        t = unittest.main(exit=False)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        logger.info(
            "\n" + "-" * 32 + "\nSuccessful test: %s", t.result.wasSuccessful()
        )

        if t.result.wasSuccessful():
            if not status["status"]:
                status["status"] = True
                status["last_change"] = timestamp
                status["message"] = ""
                send_msteams_message(True, timestamp)
        else:
            if status["status"]:
                message = ""
                for err in t.result.errors:
                    message += "<br>" + format_message(err)
                for fail in t.result.failures:
                    message += "<br>" + format_message(fail)
                status["status"] = False
                status["last_change"] = timestamp
                status["message"] = message
                logger.info(f"WebSupervisor failed!{message}")
                send_msteams_message(False, timestamp, message)

        status["last_update"] = timestamp

        time.sleep(2 * 60 * 1000)
