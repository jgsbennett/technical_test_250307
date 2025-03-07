Getting started
================
Hopefully, with only trivial dependencies, the code in this project should work for anybody with a recent python env.
If you'd like to reproduce my exact env, read on.

Python versions:
I have configured the python project to expect python >= 3.12, since that was the version running on my machine. 
Feel free to attempt to use other versions, although you may have varying levels of success.
If need be, you can manage your python versions to obtain 3.12 to reproduce my setup using pyenv:
https://python-poetry.org/docs/managing-environments/
Apparently, this should be possible with something like:
pyenv install 3.12.3
pyenv local 3.12.3  # Activate Python 3.12 for the current project

If you do not have poetry installed:
pipx install poetry
(Or as per https://python-poetry.org/docs/)

Install dependencies:
poetry install

Run tests in poetry environment
===============================
Run tests using poetry configured python environment
poetry run pytest

Alternately, a single test can be run with, for instance:
poetry run pytest .\test_car_details.py::test_vehicle_reg_details[KT17DLX]

Additional notes:
=================
Could have added "autouse" python fixtures for common setup/teardown (teardown goes after 'yield' statement). Didn't get time. Could have added sensible logging and/or addtional cleanup operations.
Currently consider that having the function scoped fixture navigate back to the home page each test is good enough.
Didn't finish testing that the multiple car_output files logic would work, would have done that next.
Sad I didn't refactor the wait_for_page_loaded() to live on the base class and enforce sensible waits being built into each new page. Would have required moving the convenience navigation functions back out, since the test currently creates an instance of the page class which would have failed it's own wait function. (I could have made it do a non-wait, but the best version of this model has the base class raise an exception by default, forcing subclasses to override the function and raising an error if they don't. Enforce good practice.)
I'd have liked to consider more error cases and test my own tests harder, perhaps consider where I could raise better error messages or detect failures, but ran out of time. The bits that DO this give a flavour of the kind of detection I think is sensible, and is what you'd typically improve over time to ensure the tests feed back WHY they're failing in a useful manner. That's step 1 to keeping the tests passing.
There weren't very many places to "wait" for other reasons, and page functions would have made further use of waits depending on the nature of what they're doing. Every function should FINISH with the wait to prove what it wanted to do was completed. In several of the existing functions, this is done by returning a page object, which runs a wait itself to prove that it is in fact now on the correct page. For other functions, there might be an explicitly coded wait of some kind.
