# Items kept in this module would likely be spread out better later, but for now, it's a useful place to store things
# which are not tests and which are not pages.
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

class WebDriver(webdriver.Chrome):
    """Handles interacting with the webdriver. Always good to wrap external dependencies to help smooth maintenance
    and ease integration."""

    # For instance, a convenience wait method
    def wait_for_element_by_id(self, id, timeout=2):
        """Waits for the given element to appear on the page. Defaults to 2 seconds."""

        return WebDriverWait(self, timeout).until(lambda x: x.find_element(By.ID, id))