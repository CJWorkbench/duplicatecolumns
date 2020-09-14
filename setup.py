#!/usr/bin/env python

from setuptools import setup

setup(
    name="duplicatecolumns",
    version="0.0.1",
    description="Duplicate columns with all their values",
    author="Adam Hooper",
    author_email="adam@adamhooper.com",
    url="https://github.com/CJWorkbench/converttexttonumber",
    packages=[""],
    py_modules=["duplicatecolumns"],
    install_requires=["pandas==0.25.0", "cjwmodule~=1.5.5"],
)
