#!/bin/bash

# devtest.sh
#
# Run tests against the source suitable for development checking.
#
# If silversearcher-ag and entr are installed, run continuous test with:
#
#   ag -l | entr ./devtest.sh
#
# The test should be run using tools installed to a virtualenv.
#
#   mkdir ~/venvs
#   virtualenv -p python3 ~/venvs/venvtest
#   . ~/venvs/venvtest/bin/activate
#   python -m pip install pytest mypy flake8
#

set -e

echo "Running pytest"
py.test-3

echo "Running mypy"
mypy comitup cli web test

echo "Running flake8"
flake8 comitup cli web test *.py

echo "Tests completed successfully"
