# Copyright (c) 2022 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#

import subprocess

import nox

pkgs = [
    "libcairo2-dev",
    "gobject-introspection",
    "libgirepository1.0-dev",
    "python3-dev",
    "libdbus-glib-1-dev",
    "libdbus-1-dev",
]

deps = [
    "pytest",
    "mock",
    "dbus-python",
    "python-networkmanager",
    "flask",
    "pygobject",
    "cachetools",
]


def missing_pkg(pkg):
    cmd = "dpkg -l {} > /dev/null".format(pkg)
    return subprocess.run(cmd, shell=True).returncode != 0


@nox.session()
def test(session):
    missings = [x for x in pkgs if missing_pkg(x)]
    if missings:
        session.error("Missing packages: %s" % format(", ".join(missings)))

    for pkg in deps:
        session.install(pkg)

    session.run("pytest")


@nox.session()
def flake8(session):
    session.install("flake8")
    session.run("flake8", "setup.py", "cli", "comitup", "web", "test")


@nox.session()
def mypy(session):
    session.install(
        "mypy",
        "types-mock",
        "types-tabulate",
        "types-pkg_resources",
        "types-Flask",
        "types-cachetools",
    )

    session.run("mypy", "cli", "comitup", "web", "test")
