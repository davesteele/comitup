
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


#            [os.unlink(os.path.join(root, x)) for x in files if x in
                

#        for base in ('.', 'test', 'comitup'):
#            for entry in os.listdir(base):
#                path = os.path.join(base, entry)
#
#                for str in (".pyc", ".coverage", ".cache", "__pycache__"):
#                    if str in entry:
#                        if os.isdir(path):
#                            shutil.rmtree(path)
#                        else:
#                            os.unlink(path)



setup(
    name='comitup',
    packages=['comitup', 'web', 'cli'],
    version='0.1',
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
            'comitup=comitup:main',
            'comitup-cli=cli:interpreter',
        ],
    },
    data_files=[
        ('/etc', ['conf/comitup.conf']),
        ('/var/lib/comitup', ['conf/comitup.json']),
        ('/etc/dbus-1/system.d', ['conf/comitup-dbus.conf']),
    ],
    install_requires=['networkmanager', 'tabulate', 'crypto', 'avahi'],
    tests_require=['pytest', 'mock'],
    cmdclass={
        'clean': MyClean,
        'test': PyTest,
    },
    author="David Steele",
    author_email="dsteele@gmail.com",
    url='https://davesteele.github.io/comitup/',
    )
