
import nox

deps = [
    "pytest",
    "mock",
    "dbus-python",
    "python-networkmanager",
    "flask",
    "pygobject",
]

@nox.session(python="3.7")
def test(session):
    for pkg in deps:
        session.install(pkg)
    session.run("pytest")
