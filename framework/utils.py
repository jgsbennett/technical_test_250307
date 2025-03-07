# Items kept in this module would likely be spread out better later, but for now, it's a useful place to store things
# which are not tests and which are not pages.
import logging
from selenium import webdriver

class WebDriver(webdriver.Chrome):
    """Handles interacting with the webdriver. Always good to wrap external dependencies to help smooth maintenance
    and ease integration."""
