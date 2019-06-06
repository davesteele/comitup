
import nox
import subprocess
import sys

pkgs = [
    "libcairo2-dev",
    "libjpeg-dev",
    "libgif-dev",
    "gobject-introspection",
    "libgirepository1.0-dev",
]

deps = [
    "pytest",
    "mock",
    "dbus-python",
    "python-networkmanager",
    "flask",
    # apt-get install libcairo2-dev libjpeg-dev libgif-dev
    # apt-get install gobject-introspection libgirepository1.0-dev
    "pygobject",
]

def missing_pkg(pkg):
    cmd = "dpkg -l {} > /dev/null".format(pkg)
    return subprocess.run(cmd, shell=True).returncode != 0

@nox.session(python="3.7")
def test(session):
    missings = [x for x in pkgs if missing_pkg(x)]
    if missings:
        print("Missing packages")
        for pkg in missings:
            print("    {}".format(pkg))
        sys.exit(1)

    for pkg in deps:
        session.install(pkg)

    session.run("pytest")
