class Page():
    """Top level class representing a page."""

    # Override in children
    URL = None

    def __init__(self, driver):
        # Look after a driver object so that the page can always interact with the browser.
        self.driver = driver

    def goto_motorway_home(self):
        self.driver.get(MotorwayHomepage.URL)

class MotorwayHomepage():
    URL = "https://motorway.co.uk/"

