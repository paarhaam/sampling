import os
from pathlib import Path
import shutil
import stat
from setuptools import setup
from setuptools.command.build_py import build_py

project_path = Path(__file__).parent


def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def remove_dirs_and_files(rm_dist=False):
    remove_dirs = []
    remove_dirs = [Path(project_path, "build")]
    remove_dirs += [str(f) for f in Path(project_path, "src").glob("**/*.exp")]
    remove_dirs += [str(f) for f in Path(project_path, "src").glob("**/*.pyd")]
    remove_dirs += [str(f) for f in Path(project_path, "src").glob("**/*.lib")]
    remove_dirs += [str(f) for f in Path(project_path, "src").glob("**/*.so")]
    if rm_dist:
        remove_dirs += [str(f) for f in Path(project_path).glob("*{0}".format("dist"))]
    remove_dirs += [str(f) for f in Path(project_path).glob("*{0}".format("egg_info"))]

    for d in remove_dirs:
        if os.path.isdir(d):
            shutil.rmtree(d, onerror=on_rm_error)
        elif os.path.isfile(d):
            os.remove(d)

remove_dirs_and_files(True)

VERSION = "0.0.1"

REQUIREMENTS = ['sobol_seq', 'numpy']
SETUP_REQUIREMENTS = []

setup(
    name="sampling",
    version=VERSION,
    description="This package implements sampling methods, usefull for simulation analysis.",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="paarhaam",
    author_email="paarhaam@yahoo.com",
    url="/depo",
    packages=["sampling"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    classifiers=["Programming Language :: Python :: 3.7"],
    install_requires=REQUIREMENTS,
    setup_requires=SETUP_REQUIREMENTS,
    cmdclass={"build_py": build_py},
    python_requires=">=3.7",
)

remove_dirs_and_files(False)
