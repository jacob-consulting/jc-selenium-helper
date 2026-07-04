# noxfile.py
import nox

PYTHONS = ["3.12", "3.13", "3.14"]


@nox.session(python=PYTHONS)
def tests(session):
    session.install("-e", ".[test]")
    session.run("pytest", "-q", *session.posargs)


@nox.session
def lint(session):
    session.install("ruff")
    session.run("ruff", "check", "src", "tests")
    session.run("ruff", "format", "--check", "src", "tests")


@nox.session
def docs(session):
    session.install("-e", ".[dev]")
    session.run("mkdocs", "build", "--strict")
