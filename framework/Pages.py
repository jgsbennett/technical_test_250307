from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
import logging

class Page(object):
    """Top level class representing a page."""

    # Override in children
    URL = None

    def __init__(self, driver):
        # Look after a driver object so that the page can always interact with the browser.
        self.driver = driver

    # Note: These are some convenience navigation methods which help bootstrap the test. I already don't like that I've
    # let this link live here, since it prevented me from refactoring some page load logic here (since a test was using
    # an instance of a page object to access this function). A poor choice retrospectively, but I'd refactor it out, I
    # just may not in the course of this technical test, and the implications aren't so severe that I MUST right now.

    def goto_motorway_home(self):
        self.driver.get(MotorwayHomepage.URL)
        # Return a page object associated with the motorway home page so that the test can interact with it.
        return MotorwayHomepage(self.driver)

class MotorwayHomepage(Page):
    URL = "https://motorway.co.uk/"

    # Store selectors for elements we care about at class top level so that they're easy to modify if any change later.
    # For the input field, handily there is an ID
    VRM_INPUT_ID = "vrm-input"
    # For the submit button, there are actually two buttons on the page. Look for the one that exists inside a div
    # that looks roughly like this. (Cut the weird text on the end in case that's tied to versions etc...
    # I'm taking a guess this would be relatively stable, but I might want to consult with devs, or ideally get an ID
    # added for this component too, if that's an option.
    VRM_SUBMIT_CSS = "div[class^='HomepageVRM__component'] button[type='submit']"
    # If there is an error, it's briefly displayed here
    VEHICLE_ERROR_CSS = "div[class^='InfoBox-module']"

    def __init__(self, *args, **kwargs):
        super(MotorwayHomepage, self).__init__(*args, **kwargs)
        # Logs which pages we navigate to, taking note of child classes. Helps diagnose any issues
        logging.info("Loading page: %s" % self.__class__)

        # The page might be loading. Let's wait until at least the VRM input is available before we allow the test to
        # proceed.
        # Will proceed as soon as it is.
        # IMPORTANT!
        # At the moment, this function allows various other calls on the page to ASSUME that the elements will be
        # available, i.e: we can just call find_element() and they should be loaded. Any time they're missing would be
        # a bug, and so we should fail, so just using find_element() is reasonable.
        # For any non-static elements, we should implement their own "waits" in the functions that use them.
        self.wait_for_page_loaded()

    # TODO: Really I'd like to move this to a "wait_for_page_loaded()" function on the parent, which always gets
    # called, utilising an element that the child class specifies that the presence indicates that the page is ready
    # to be interacted with.
    # For now, it's defined on each subclass, since there's only two, but it's ripe for a refactor to ensure all pages
    # impliment this goodness to prevent later flakiness.
    def wait_for_page_loaded(self):
        self.driver.wait_for_element_by_id(id=self.VRM_INPUT_ID)

    def submit_vehicle_reg(self, vehicle_reg):
        """Submits the vehicle reg and returns the next page."""
        logging.info("Submitting vehicle details: %s" % vehicle_reg)
        self.driver.find_element(by=By.ID, value=self.VRM_INPUT_ID).send_keys(vehicle_reg)
        button = self.driver.find_element(by=By.CSS_SELECTOR, value=self.VRM_SUBMIT_CSS)
        button.submit()
        # Note that when we navigate, the page checks that it loads itself. If for any reason, the vehicle isn't found,
        # We won't find the elements that the page expects, and so will throw an error.
        # Later, the utility framework OR the tests could try/catch and return nicer error messages when this happens.
        try:
            return MotorwayResults(self.driver)
        except TimeoutException as e:
            # A common reason for this, is if the vehicle reg was not found. Let's check for that common case and give
            # a nice error if so. Otherwise, simply re-raise the error.
            try:
                error_message = self.find_failure_message()
                if "Did we get the reg right?" in error_message:
                    logging.info("Found error message on page.")
                    # Raise the nicer error message for the more predictable failure.
                    raise AssertionError("Vehicle reg not found on motorway.co.uk: %s" % vehicle_reg)
            except Exception as sub_e:
                logging.info(
                    "Unable to detect car reg failure message. Some other error is possible. Sub error was: %s" % sub_e
                )
                # Raise the original error message, since that's how we ended up here.
                raise e

    # Techincally, this error message appears on the home page. We currently only ever run into it if we've attempted
    # to wait for a navigation, by which time I'm confident it ought to be here if it's going to be.
    # It does disappear fairly quickly afterwards, so there's a potential timing issue here. Unclear if there's any other
    # evidence left behind in this case that we could check instead. It does mean that if we increased the default wait
    # for navigating we might miss this. We could definitely refactor the "submit" function to implement a different
    # wait loop which would EITHER detect the success page OR the error immediately, but I'm leaving that out of scope
    # for this exercise, since it's reliable for my purposes.
    def find_failure_message(self):
        return self.driver.find_element(By.CSS_SELECTOR, self.VEHICLE_ERROR_CSS).text


class MotorwayResults(Page):

    # Unclear if it's ever valid to navigate straight here, but I'll update the URL here nevertheless.
    URL = "https://motorway.co.uk/mileage"

    # Another element with a nice ID
    MILEAGE_INPUT_ID = "mileage-input"
    # Another where I've taken a stab at a CSS selector I hope would be fairly stable.
    MAKE_AND_MODEL_CSS = "h1[class^='HeroVehicle__title']"
    # Sadly, this one is even uglier. This CSS will always grab the first element in the details box. So long as the
    # year remains the first thing they display, this will be fine.
    YEAR_CSS = "ul[class^='HeroVehicle__details'] li"

    # TODO: Again, likely refactor, as described above. Duplicate code.
    def __init__(self, *args, **kwargs):
        super(MotorwayResults, self).__init__(*args, **kwargs)
        self.wait_for_page_loaded()

    # TODO: Again, likely refactor, as described above. Duplicate code.
    def wait_for_page_loaded(self):
        self.driver.wait_for_element_by_id(id=self.MILEAGE_INPUT_ID)

    def get_make_and_model(self):
        return self.driver.find_element(By.CSS_SELECTOR, value=self.MAKE_AND_MODEL_CSS).text

    def get_year(self):
        return self.driver.find_element(By.CSS_SELECTOR, value=self.YEAR_CSS).text

    def get_car_details(self):
        # I'd strongly consider making this a Car or CarDetails class in its own right if we started interacting heavily
        # with them. As it is, for this tiny set of tests, it's not necessary.
        return {
            "make_and_model": self.get_make_and_model(),
            "year": self.get_year()
        }
