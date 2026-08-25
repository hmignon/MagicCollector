import sys
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from invoke import task


@task(name="lint", aliases=["l"])
def lint(c):
    linters = {
        "Black": "black .",
        "Isort": "isort .",
        "Ruff": "ruff check . --fix",
        "Django checks": "python manage.py check",
        "Django migrations": "python manage.py makemigrations --check --dry-run",
    }

    for linter, command in linters.items():
        run_linter(c, linter, command)

    print("\nAll done!")


def run_linter(c, header, command):
    print(f"{header} {'.' * (45 - len(header))}", end="")
    result = c.run(command, hide=True, warn=True)
    if result.ok:
        print(" OK")
    else:
        print(" FAILED\n")
        print(result.stdout)
        exit()


@task(name="test", aliases=["t"])
def test(c):
    c.run("python manage.py test")


@task(name="testfail", aliases=["tf"])
def test_fail(c):
    c.run("python manage.py test --failfast")


@task(name="coverage", aliases=["cov"])
def coverage(c):
    c.run("coverage run --source='.' manage.py test")
    c.run("coverage report")
    c.run("coverage html")


@task(name="runserver", aliases=["rs"])
def run(c):
    c.run("python manage.py migrate")
    c.run("python manage.py runserver")
