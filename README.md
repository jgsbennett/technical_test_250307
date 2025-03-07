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