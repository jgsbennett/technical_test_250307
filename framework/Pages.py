from selenium.webdriver.common.by import By

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
    # VRM_SUBMIT_CSS = "#vrm-input"

    def __init__(self, *args, **kwargs):
        super(MotorwayHomepage, self).__init__(*args, **kwargs)

        # The page might be loading. Let's wait until at least the VRM input is available before we allow the test to
        # proceed.
        # Will proceed as soon as it is.
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
        self.driver.find_element(by=By.ID, value=self.VRM_INPUT_ID).send_keys(vehicle_reg)
        button = self.driver.find_element(by=By.CSS_SELECTOR, value=self.VRM_SUBMIT_CSS)
        button.submit()
