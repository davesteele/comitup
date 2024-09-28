#!/usr/bin/python3
#
# Copyright (c) 2022 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#

"""
devtest.py

This creates a  virtual environment, and runs a number of test environments
against the comitup code.

The venv is persistent, and the tests run in parallel, so this is much quicker
than tox or nox.
"""

import subprocess
import sys
import venv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

envpath: Path = Path(__file__).resolve().parent / ".devenv"
pythonpath: str = str(envpath / "bin" / "python")


pkgs: List[str] = [
    "pytest",
    "mypy",
    "flake8",
    "black",
    "isort",
    "cachetools",
    "flask",
    "types-tabulate",
    "types-Flask",
    "types-cachetools",
]

targets: str = "comitup web cli test devtest.py setup.py"


def mkcmd(cmd: str) -> List[str]:
    return [str(pythonpath), "-m"] + cmd.split()


def run(cmd: str) -> subprocess.CompletedProcess:
    cp = subprocess.run(
        mkcmd(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    return cp


print("# Tests starting")

if not envpath.exists():
    print("# Creating virtual environment")

    virtenv = venv.EnvBuilder(
        system_site_packages=True, symlinks=True, with_pip=True
    )
    virtenv.create(str(envpath))

    print("# Installing packages")

    for pkg in pkgs:
        cp = run("pip install " + pkg)
        print("Running", " ".join(cp.args))
        print(cp.stdout.decode())


tests: List[str] = [
    "black --check {}".format(targets),
    "isort --check {}".format(targets),
    "mypy {}".format(targets),
    "flake8 {}".format(targets),
    "pytest",
]

executor = ThreadPoolExecutor(max_workers=5)

fail = False
for result in executor.map(lambda x: run(x), tests):
    print("#####################################")
    print("# Running {}".format(" ".join(result.args)))
    print(result.stdout.decode())
    print("#####################################")
    print()
    if result.returncode:
        fail = True

if fail:
    print("# ERROR(S) ENCOUNTERED")
    sys.exit(1)

print("# Tests complete")
