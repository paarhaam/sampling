import os
import shutil
import stat
import sys
import re
from pathlib import Path
import platform
import invoke

VENV = Path(".").parent / "venv"
VENV_PATH = VENV / "Scripts"
VENV_PYTHON = VENV_PATH / "python"
VENV_PIP = VENV_PATH / "pip3.7"
VENV_PYTEST = VENV_PATH / "pytest"
VENV_COVERAGE = VENV_PATH / "coverage-3.7"
VENV_PYLINT = VENV_PATH / "pylint"
VENV_BLACK = VENV_PATH / "black"
VENV_MYPY = VENV_PATH / "mypy"
VENV_PYFLAKES = VENV_PATH / "pyflakes"


def on_rm_error(func, path, exc_info) -> None:
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)

@invoke.task
def uninstall(context):
    """ Uninstall package to scan test coverage. """

    context.run(f"{VENV_PIP} uninstall -y sampling", echo=True)


@invoke.task
def install(context):
    """ Install package. """

    for wheel in Path(Path(__file__).parent / "dist").glob("*.whl"):
        context.run(f"{VENV_PIP} install {wheel}", echo=True)


@invoke.task
def scan(context):
    """ Runs code coverage """

    context.run(f"{VENV_PYTEST} --color=yes --verbose --cov-report=xml --cov=src", echo=True)
    context.run(f"{VENV_COVERAGE} report --fail-under=80 -m", echo=True)

@invoke.task
def test(context):
    """ Runs unit test """

    context.run(f"{VENV_PYTEST} test", echo=True)


@invoke.task
def setversion(context, version="development"):
    """ Sets __version in __init__.py """

    for dunder in Path("src").glob("**/__init__.py"):
        dunder.write_text(
            re.sub(
                r"__version__\ *=\ *\".+\"",
                f'__version__ = "{version}"',
                dunder.read_text(),
            )
        )
        print(f" Version set to '{version}' in '{dunder}'")

    setuppy = Path("setup.py")
    setuppy.write_text(
        re.sub(r"VERSION\ *=\ *\".+\"", f'VERSION = "{version}"', setuppy.read_text())
    )

    print(f" Version set to '{version}' in '{setuppy}'")


@invoke.task
def build(context):
    """ Builds a wheel and source distribution archive """

    context.run(f"{VENV_PYTHON} setup.py bdist_wheel")


@invoke.task
def publish(context):
    """ Publish to artifactory """

    for filepath in Path(Path(__file__).parent / "dist").glob("*.whl"):
        context.run(f" ./jfrog rt upload {filepath} your/URL")

@invoke.task
def clean(context, deps=False):
    """ Clean up repo and uninstall package"""
    current_dir = os.path.dirname(os.path.realpath(__file__))
    for pattern in [
        "dist/",
        "build/",
        ".mypy_cache",
        ".pytest_cache/",
        ".coverage",
        "coverage.xml",
        ".scannerwork",
        "__pycache__/",
    ]:
        if os.path.isfile(os.path.join(current_dir, pattern)):
            os.remove(os.path.join(current_dir, pattern))
        elif os.path.isdir(os.path.join(current_dir, pattern)):
            shutil.rmtree(os.path.join(current_dir, pattern), onerror=on_rm_error)

    if deps:
        context.run(f"virtualenv --clear env", echo=True)
        context.run(f"{VENV_PIP} install -r requirements.txt", echo=True)


@invoke.task
def fmt(context):
    """ Formats using Black """

    context.run(f"{VENV_BLACK} --verbose ./src ./test ./setup.py ./tasks.py", echo=True)


@invoke.task
def fmtcheck(context):
    """ Black format checker """

    context.run(f"{VENV_BLACK} --check --diff --verbose ./src ./test ./setup.py ./tasks.py", echo=True)


@invoke.task
def typecheck(context):
    """ Runs type checker """
    def mypy(context, directory):
        for dirpath, _, filenames in os.walk(os.path.join(os.getcwd(), directory)):
            for filename in filenames:
                if re.match(r"^.*\.py$", filename):
                    context.run(f"{VENV_MYPY} {os.path.join(dirpath, filename)}", echo=True)

    mypy(context, "src")
    mypy(context, "test")


@invoke.task
def lint(context):
    """ Runs pyflakes and pylint """


    context.run(f"{VENV_PYFLAKES} ./src ./test", echo=True)

    def pylint(context, path):
        pylint_ret = context.run(f"{VENV_PYLINT} {path}", echo=True, warn=True).exited
        if pylint_ret and ((1 & pylint_ret) or (2 & pylint_ret) or (32 & pylint_ret)):
            sys.exit(pylint_ret)

    pylint(context, "./src")
    pylint(context, "./test")
