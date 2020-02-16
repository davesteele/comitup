
import nox
import subprocess

pkgs = [
    "libcairo2-dev",
    "gobject-introspection",
    "libgirepository1.0-dev",
    "python3-dev",
]

deps = [
    "pytest",
    "mock",
    "dbus-python",
    "python-networkmanager",
    "flask",
    "pygobject",
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
    session.run("flake8", "setup.py", "cli", "comitup", "web")
