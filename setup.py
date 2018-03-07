from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Preparing long description from README.
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="versionml",
    version="1.0.0",
    description="Version control system for your machine learning projects.",
    long_description=long_description,
    url="https://versionml.com",
    author="Team VersionML",
    author_email="author@versionml.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="version control release management data science \
    machine learning development",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=["tinydb", "docopt", "gitpython", "uuid", "terminaltables"],
    entry_points={
        "console_scripts": [
            "versionml=versionml.cli:main",
        ],
    }
)