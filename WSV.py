"""Test WebSupervisor in North Europe and Australia.

Open WSV - check browser title
Login - check loggged user name
Go to units - count units
"""

import logging
import os
import platform
import unittest
from datetime import datetime

import pymsteams
import yaml
from parameterized import parameterized_class
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import (
    config,
    ERP_url,
    status_file,
    send_to_teams,
    test_enabled,
    xpath_login,
    xpath_login_id,
    xpath_password,
    xpath_units,
    xpath_username,
)
from secrets import teams_webhook, wsv_account

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(message)s",
    filename="WSV.log",
    level=logging.INFO,
    filemode="w",
)

# pylint: disable=no-member


@parameterized_class(
    ("location", "url", "display_name", "unit_count", "user_name", "user_password"),
    [config[i] + wsv_account[i] for i in range(0, len(config))],
)
class TestWSV(unittest.TestCase):
    """WebSupervisor tests."""

    def setUp(self):
        """Test fixture - open the browser."""
        _LOGGER.info(
            "\n" + "-" * 32 + "\nSetting test up for %s\n" + "-" * 32, self.location
        )
        self.browser = webdriver.Chrome()
        self.browser.maximize_window()
        self.browser.implicitly_wait(60)

    def tearDown(self):
        """Close the browser window."""
        _LOGGER.info("Tearing down test for %s", self.url)
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
        elements = None
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
        """Test case."""
        # Open WebSupervisor, check page title
        self.browser.get(self.url)
        _LOGGER.info("Testing website title")
        _LOGGER.info("Title: %s", self.browser.title)
        self.assertIsNotNone(self.browser.title, "Can't find the webpage tille. WSV down?")
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
        _LOGGER.info("Testing logged user name")
        try:
            login_id = self.wait_find_element_by_xpath(60, xpath_login_id).text
        except (NoSuchElementException, AttributeError):
            login_id = None
        _LOGGER.info("Logged user: %s", login_id)
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
        _LOGGER.info("Testing list of units")
        for row in table_rows:
            unit = row.find_elements_by_tag_name("td")[2]
            if unit.text != "":
                units.append(unit.text)
                _LOGGER.info("Unit: %s", unit.text)
        _LOGGER.info("Found %d units", len(units))
        self.assertTrue(
            len(units) >= self.unit_count,
            f"Number of units does not match. Found {len(units)}, "
            f"expected {self.unit_count}",
        )

# class TestERP(unittest.TestCase):
#     """ERP tests."""

#     def setUp(self):
#         """Test fixture - open the browser."""
#         _LOGGER.info("\n" + "-" * 32 + "\nSetting test up for ERP\n" + "-" * 32)
#         self.browser = webdriver.Chrome()
#         self.browser.maximize_window()
#         self.browser.implicitly_wait(60)

#     def tearDown(self):
#         """Close the browser window."""
#         _LOGGER.info("Tearing down test for ERP")
#         self.browser.quit()

#     def wait_find_element_by_xpath(self, maxTimeOut, locator):
#         """In case the element got destroyed, wait for it to be recreated."""
#         element = None
#         try:
#             WebDriverWait(
#                 self.browser,
#                 maxTimeOut,
#                 ignored_exceptions=[StaleElementReferenceException],
#             ).until(EC.presence_of_element_located((By.XPATH, locator)))
#             element = self.browser.find_element_by_xpath(locator)
#         except Exception:
#             raise NoSuchElementException(
#                 "Exception occurred during object identification."
#             )
#         return element

#     def test_ERP(self):
#         """Test case."""
#         # Open ERP, check page title
#         self.browser.get(ERP_url)
#         _LOGGER.info("Testing website title")
#         _LOGGER.info("Title: %s", self.browser.title)
#         self.assertIn(
#             "Dashboard -- Finance and Operations",
#             self.browser.title,
#             "The webpage title does not match. "
#             f'Expected "Dashboard -- Finance and Operations", found "{self.browser.title}"',
#         )


def TeamsMessage(state, timestamp, message=""):
    """Post error message to Teams."""
    # if platform.system() == "Windows":
    if not send_to_teams:
        if state:
            print("Automated WSV alert canceled (beta)")
            print(f"{timestamp}: WSV is running normaly.")
        else:
            print("Automated WSV Alert (beta)")
            print(
                f"{timestamp}: The automated WSV checking script has failed.{message}"
            )
    else:
        myTeamsMessage = pymsteams.connectorcard(teams_webhook)
        if state:
            myTeamsMessage.title("Automated WSV alert canceled (beta)")
            myTeamsMessage.text(f"{timestamp}: WSV is running normaly.")
        else:
            myTeamsMessage.title("Automated WSV Alert (beta)")
            myTeamsMessage.text(
                f"{timestamp}: The automated WSV checking script has failed.{message}"
            )
            if "North_Europe" in message:
                myTeamsMessage.addLinkButton(
                    "Check WSV in North Europe!", "https://www.websupervisor.net"
                )
            if "Australia" in message:
                myTeamsMessage.addLinkButton(
                    "Check WSV in Australia!", "https://aus.websupervisor.net"
                )
        myTeamsMessage.send()


def FormatMessage(msg):
    """Format the message."""
    test = msg[0]._testMethodName
    err = msg[1]
    assertion = err[err.find("AssertionError") + 15:]
    return test + assertion[assertion.find(":") + 1:]


if __name__ == "__main__":
    if test_enabled:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with Display(visible=0, size=(1920, 1080)) as display:
            t = unittest.main(exit=False)
            # if not t.result.wasSuccessful():  # Try again
            #     t = unittest.main(exit=False)
            with open(status_file, "r") as f:
                status = yaml.full_load(f)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            _LOGGER.info(
                "\n" + "-" * 32 + "\nSuccessful test: %s", t.result.wasSuccessful()
            )
            if t.result.wasSuccessful():
                if not status["status"]:
                    status["status"] = True
                    status["last_change"] = timestamp
                    status["message"] = ""
                    TeamsMessage(True, timestamp)
            else:
                if status["status"]:
                    message = ""
                    for err in t.result.errors:
                        message += "<br>" + FormatMessage(err)
                    for fail in t.result.failures:
                        message += "<br>" + FormatMessage(fail)
                    status["status"] = False
                    status["last_change"] = timestamp
                    status["message"] = message
                    _LOGGER.info(f"WebSupervisor failed!{message}")
                    TeamsMessage(False, timestamp, message)
            status["last_update"] = timestamp
            with open(status_file, "w") as f:
                yaml.dump(status, f)
