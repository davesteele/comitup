# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

from setuptools import setup

setup(
    name="comitup",
    packages=["comitup", "web", "cli"],
    version="1.38",
    description="Remotely manage wifi connections on a headless computer",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved "
        + ":: GNU General Public License v2 or later (GPLv2+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: System :: Networking",
    ],
    entry_points={
        "console_scripts": [
            "comitup=comitup.comitup:main",
            "comitup-cli=cli.comitupcli:main",
            "comitup-web=web.comitupweb:main",
        ],
    },
    options={
        "build_scripts": {
            "executable": "/usr/bin/python3",
        },
    },
    data_files=[
        ("/etc", ["conf/comitup.conf"]),
        ("/var/lib/comitup", ["conf/comitup.json"]),
        ("/etc/dbus-1/system.d", ["conf/comitup-dbus.conf"]),
        (
            "/usr/share/comitup/web/templates",
            [
                "web/templates/index.html",
                "web/templates/connect.html",
                "web/templates/confirm.html",
            ],
        ),
        (
            "/usr/share/comitup/web/templates/css",
            [
                "web/templates/css/uikit.css",
                "web/templates/css/uikit-rtl.css",
                "web/templates/css/uikit.min.css",
                "web/templates/css/uikit-rtl.min.css",
            ],
        ),
        (
            "/usr/share/comitup/web/templates/js",
            [
                "web/templates/js/uikit",
                "web/templates/js/uikit-icons",
                "web/templates/js/blink.js",
            ],
        ),
        (
            "/usr/share/comitup/web/templates/images",
            [
                "web/templates/images/ledon.gif",
                "web/templates/images/ledoff.gif",
            ],
        ),
        (
            "/usr/share/comitup/dns",
            [
                "conf/dns-hotspot.conf",
                "conf/dns-connected.conf",
            ],
        ),
    ],
    install_requires=[
        "cachetools",
        "jinja2",
        "dbus-python",
        "pygobject",
        "flask",
        "python-networkmanager",
        "pycairo",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "mock"],
    author="David Steele",
    author_email="steele@debian.org",
    url="https://davesteele.github.io/comitup/",
)
