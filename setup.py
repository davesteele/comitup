
#
# Copyright 2016 David Steele <steele@debian.org>
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
    version='0.4',
    description="Copy a remote file using multiple SSH streams",
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
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
            'executable': '/usr/bin/python2.7',
        },
    },
    data_files=[
        ('/etc', ['conf/comitup.conf']),
        ('/var/lib/comitup', ['conf/comitup.json']),
        ('/etc/dbus-1/system.d', ['conf/comitup-dbus.conf']),
        ('/usr/share/comitup/web', ['web/comitupweb.conf']),
        ('/usr/share/comitup/web/templates',
            [
                'web/templates/index.html',
                'web/templates/connect.html',
                'web/templates/confirm.html',
            ]
        ),
    ],
    install_requires=[
        'jinja2',
    ],
    tests_require=['pytest', 'mock'],
    cmdclass={
        'clean': MyClean,
        'test': PyTest,
    },
    author="David Steele",
    author_email="steele@debian.org",
    url='https://davesteele.github.io/comitup/',
    )
