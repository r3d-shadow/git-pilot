#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="git-pilot",
    version="0.2.0",
    description="A CLI tool to sync and update Git workflows and configurations across multiple repositories efficiently and consistently.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="r3d-shadow",
    python_requires=">=3.6",
    packages=find_packages(include=["src", "src.*"]),
    install_requires=[
        "PyGithub==2.6.1",
        "PyYAML==6.0.2",
        "Jinja2==3.1.6",
        "rich==14.0.0",
        "colorama==0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "git-pilot = src.main:main",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
    ],
    license="Apache License 2.0",
)
