#!/usr/bin/python3


"""
devtest.py

This creates a  virtual environment, and runs a number of test environments
against the comitup code.

The venv is persistent, so the tests run quicker than in tox or nox.
"""

import subprocess
import sys
import venv
from pathlib import Path
from typing import List


envpath: Path = Path(__file__).resolve().parent / ".devenv"
pythonpath: str = str(envpath / "bin" / "python")


pkgs: List[str] = [
    "pytest",
    "mypy",
    "flake8",
    "types-mock",
    "types-tabulate",
    "types-pkg_resources",
    "types-Flask",
    "types-cachetools",
]

targets: str = "comitup web cli test devtest.py setup.py"


def mkcmd(cmd: str) -> List[str]:
    return [str(pythonpath), "-m"] + cmd.split()


def run(cmd: str) -> int:
    cp = subprocess.run(mkcmd(cmd))

    return cp.returncode


def runtest(test: str) -> int:

    print("# Running {}".format(test.split()[0]))

    return run(test)


print("# Tests starting")

if not envpath.exists():
    print("# Creating virtual environment")

    virtenv = venv.EnvBuilder(
        system_site_packages=True, symlinks=True, with_pip=True
    )
    virtenv.create(str(envpath))

    print("# Installing packages")

    run("pip install " + " ".join(pkgs))


tests: List[str] = [
    "pytest",
    "mypy {}".format(targets),
    "flake8 {}".format(targets),
]

if any([runtest(test) for test in tests]):
    print("# ERROR(S) ENCOUNTERED")
    sys.exit(1)

print("# Tests complete")
