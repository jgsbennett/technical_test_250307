import logging
import re
import csv
import pytest
import os
import pathlib
from .framework.utils import WebDriver
from .framework.Pages import Page

# Define input and output locations. Could easily make these configurable by command line args, but for now, let's
# just say we'll read anything in these dirs.
INPUT_FILES_DIR = pathlib.Path(pathlib.Path(__file__).parent, "input_files")
EXPECTATIONS_FILES_DIR = pathlib.Path(pathlib.Path(__file__).parent, "expectation_files")

def get_vehicle_regs_from_file(file_path):
    """Reads a single file and returns the list of vehicle registrations found."""
    logging.debug("Looking for vehicle regs in %s" % file_path)
    with open(pathlib.Path(INPUT_FILES_DIR, file_path)) as f:
        # If this file was massive, we might consider reading this in chunks. For now, let's read it in one go.
        file_string = f.read()
        # Use regular expression to grab all license plates from the file.
        # Vehicle registration plate patters are apparently
        # Begin with two letters
        # then two numbers
        # Optionally allow a space.
        # Finish with three letters.
        pattern = r"[A-Z]{2}[0-9]{2}[ ]?[A-Z]{3}"
        prog = re.compile(pattern)
        vehicle_regs = prog.findall(string=file_string)
        logging.debug("Found vehicle regs: %s" % vehicle_regs)
        # Note: Choosing not to clean up whitespace in the registrations. We could do that, if it matters. As it is,
        # It seems reasonable to submit both with/without the space.
    # Return the "set" of the regs to ensure there are no duplicates.
    # In the future, we might decide we need multiple regular expressions if it turns out the one above is insufficient
    # on its own. Collecting regs into a set allows us to also stop it mattering if a reg matches multiple expressions
    # in that case.
    return set(vehicle_regs)

def get_vehicle_regs_from_input_files():
    """Retrieves the vehicle registrations from the input files."""
    vehicle_regs = []
    input_file_names = [f for f in os.listdir(INPUT_FILES_DIR) if pathlib.Path(INPUT_FILES_DIR, f).is_file()]
    logging.info("Found %s input files." % len(input_file_names))

    for file_path in input_file_names:
        logging.info("Reading car reg from %s" % file_path)
        # File could be a dir, but I'm happy that we'll just error if it is. If we want to support subdirs later,
        # we can edit this and recursively grab files.
        vehicle_regs.extend(get_vehicle_regs_from_file(file_path=file_path))
    logging.info("Found %s registrations in %s files" % (len(vehicle_regs), len(input_file_names)))
    return vehicle_regs

logging.info("Running test suite setup")
# Fixtures are good for lots of things in pytest, however, we want to know the list of car reg's before we get to the
# pytest.param fixture setup, hence, we must read the input files at import time so that we can dynamically generate
# tests for each reg.
vehicle_regs = get_vehicle_regs_from_input_files()
logging.info("Found vehicle_regs: %s" % vehicle_regs)

# We may want to add some better check here to ensure this is vaguely working. For now, ensuring we got at least one
# vehicle registration returned counters the case where everything is broken and we run no tests at all.
# This assert would cause the process to exit with an error code if there are no regs, allowing CI to detect and fail.
assert len(vehicle_regs) > 0, "No vehicle registrations found in input files."

# Session scoped variable since we only want the driver to be opened once.
# It's possible that there could be errors that killed the browser etc...
# If we were concerned about this we could always add a function-scoped fixture which checked for the healthy state
# of the browser window and refreshed the driver if needed.
@pytest.fixture(scope="session")
def web_driver():
    # Here, we could do some detection/choices about which browser to use.
    try:
        webdriver = WebDriver()
    except Exception as e:
        logging.error("Failed to load webdriver. You may need some additional config to ensure this works")
        # We could attempt to diagnose or try harder here. For now, out of scope. Only handling to demonstrate we could
        # As it is, just re-raise.
        raise
    return WebDriver()

@pytest.fixture()
def motorway_home_page(web_driver):
    # For now, there's a convenience function on top level Page ot navigate to a specific page.
    return Page(web_driver).goto_motorway_home()

# Only need to load expected data once.
@pytest.fixture(scope="session")
def expected_data():
    return get_vehicle_regs_from_input_files()

@pytest.mark.parametrize("vehicle_reg", [(v) for v in vehicle_regs])
def test_vehicle_reg_details(vehicle_reg, motorway_home_page, expected_data):
    logging.info("Running test for vehicle_reg: %s" % vehicle_reg)
    results_page = motorway_home_page.submit_vehicle_reg(vehicle_reg)
    page_car_details = results_page.get_car_details()

    logging.info("Data for car was: %s" % page_car_details)
    compare_page_details_and_expected_details(vehicle_reg, page_car_details, expected_data)

def get_vehicle_regs_from_input_files():
    """Retrieves the expected vehicle data for comparisons in the tests."""
    vehicle_details = {}
    output_file_names = [f for f in os.listdir(EXPECTATIONS_FILES_DIR) if pathlib.Path(EXPECTATIONS_FILES_DIR, f).is_file()]
    logging.info("Found %s output files." % len(output_file_names))

    for file_path in output_file_names:
        logging.info("Reading car details from %s" % file_path)
        # Again, file could be a dir, but I'm happy that we'll just error if it is. If we want to support subdirs later,
        # we can edit this and recursively grab files.
        new_details = load_expected_data_file(file_path=file_path)
        # TODO: Check if any details mismatch. If so, error.
        for car in new_details:
            assert car not in vehicle_details, "Same car details feature in two output files. Currently not supported."
        # If they're all new, let's update
        vehicle_details.update(new_details)

    logging.info("Found %s details in %s files" % (len(vehicle_details), len(output_file_names)))
    return vehicle_details

def load_expected_data_file(file_path):
    # Let's store the details in a dictionary. Tests can query it later.
    details_dict = {}
    logging.debug("Looking for vehicle details in %s" % file_path)
    with open(pathlib.Path(EXPECTATIONS_FILES_DIR, file_path)) as f:
        # If this file was massive, we might consider reading this in chunks. For now, let's read it in one go.
        csv_reader = csv.reader(f)
        # Skip the first row, since it contains the header etc... (Let's check this is true
        header_line = next(csv_reader)
        assert header_line[0] == "VARIANT_REG"
        logging.info("Expectation file matches the expected format.")
        for row in csv_reader:
            logging.debug("Found details: %s" % row)
            assert len(row) == 3, "Expectation CSV not expected format. Row should have 3 components. %s" % row
            # Use the first element as the key to the dictionary. Store the two remaining fields (make/model and year)
            # as a tuple.
            # Check it has the expected format, since we assume that it does later. If it ever doesn't, we'd need to
            # update the assumption
            assert len(row[0]) == 8 # Two letters, two numbers, space, three letters.
            details_dict[row[0]] = (row[1], row[2])
    return details_dict

def compare_page_details_and_expected_details(car_reg, page_details, expected_details):
    # First thing is to check whether the provided car reg includes the space or not. Currently, sometimes it doesn't.
    # Sanitize it. All the car regs in the expected file do currently, so we've set this as a requirement.
    # However, we didn't sanitise it on input, since it's potentially valid test case data.
    if len(car_reg) == 7:
        car_reg = car_reg[0:4] + " " + car_reg[4:]
    logging.info("Looking for details")
    assert car_reg in expected_details, "Could not find car reg %s in expected data: %s" % (car_reg, expected_details)
    car_expected_details = expected_details[car_reg]
    assert car_expected_details[0] == page_details["make_and_model"]
    assert car_expected_details[1] == page_details["year"]