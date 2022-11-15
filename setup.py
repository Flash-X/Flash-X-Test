"""Build and installation script for flashxtest."""

# standard libraries
import re
from setuptools import setup, find_packages

# get long description from README
with open("README.rst", mode="r") as readme:
    long_description = readme.read()

with open("FlashXTest/__meta__.py", mode="r") as source:
    content = source.read().strip()
    metadata = {
        key: re.search(key + r'\s*=\s*[\'"]([^\'"]*)[\'"]', content).group(1)
        for key in ["__pkgname__", "__version__", "__authors__", "__license__"]
    }

# core dependencies - click, docker, singularity
DEPENDENCIES = ["click", "six", "argparse", "pyyaml"]

setup(
    name=metadata["__pkgname__"],
    version=metadata["__version__"],
    author=metadata["__authors__"],
    license=metadata["__license__"],
    packages=find_packages(where="./"),
    package_dir={"": "./"},
    package_data={
        "": [
            "backend/FlashTest/ERROR",
            "backend/FlashTest/error.sh",
            "backend/FlashTest/exeScript",
            "backend/FlashTest/configBase",
            "backend/FlashTest/configTemplate",
            "backend/FlashTest/scripts/changeInfoFiles",
            "backend/FlashTest/scripts/restarttest/restarttest.sh",
        ]
    },
    scripts=["FlashXTest/flashxtest"],
    include_package_data=True,
    long_description=long_description,
    classifiers=["Programming Language :: Python :: 3.8"],
    install_requires=DEPENDENCIES,
)
