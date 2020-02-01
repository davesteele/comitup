
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
from distutils.command.clean import clean
from setuptools.command.test import test

import os
import shutil
import sys


class PyTest(test):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        test.finalize_options(self)

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


class MyClean(clean):
    def run(self):
        clean.run(self)

        for root, dirs, files in os.walk('.'):
            [shutil.rmtree(os.path.join(root, x)) for x in dirs if x in
                (".pyc", ".coverage", ".cache", "__pycache__",
                 "comitup.egg-info")]

            for file in files:
                for match in (".pyc", ".cache", ".coverage"):
                    if match in file:
                        os.unlink(os.path.join(root, file))


setup(
    name='comitup',
    packages=['comitup', 'web', 'cli'],
    version='1.10',
    description="Remotely manage wifi connections on a headless computer",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved ' +
        ':: GNU General Public License v2 or later (GPLv2+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: System :: Networking',
    ],
    entry_points={
        'console_scripts': [
            'comitup=comitup.comitup:main',
            'comitup-cli=cli.comitupcli:interpreter',
            'comitup-web=web.comitupweb:main',
        ],
    },
    options={
        'build_scripts': {
            'executable': '/usr/bin/python3',
        },
    },
    data_files=[
        ('/etc', ['conf/comitup.conf']),
        ('/var/lib/comitup', ['conf/comitup.json']),
        ('/etc/dbus-1/system.d', ['conf/comitup-dbus.conf']),
        ('/usr/share/comitup/web/templates',
            [
                'web/templates/index.html',
                'web/templates/connect.html',
                'web/templates/confirm.html',
            ]
        ),  # noqa
        ('/usr/share/comitup/web/templates/css',
            [
                'web/templates/css/uikit.css',
                'web/templates/css/uikit-rtl.css',
                'web/templates/css/uikit.min.css',
                'web/templates/css/uikit-rtl.min.css',
            ]
        ),  # noqa
        ('/usr/share/comitup/web/templates/js',
            [
                'web/templates/js/uikit.min.js',
                'web/templates/js/uikit-icons.min.js',
            ]
        ),  # noqa
        ('/usr/share/comitup/dns',
            [
                'conf/dns-hotspot.conf',
                'conf/dns-connected.conf',
            ]
        ),  # noqa
    ],
    install_requires=[
        'jinja2',
    ],
    setup_requires=["pytest-runner"],
    tests_require=['pytest', 'mock'],
    cmdclass={
        'clean': MyClean,
        'test': PyTest,
    },
    author="David Steele",
    author_email="steele@debian.org",
    url='https://davesteele.github.io/comitup/',
    )
