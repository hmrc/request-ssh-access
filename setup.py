#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
import os


requires = ["requests"]


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name="request-ssh-access",
    author="HRMC Platform Security",
    version="0.0.1",
    description="Helper utility to create Vault-signed SSH certificates",
    url="https://github.com/hmrc/request-ssh-access/",
    long_description=read("README.md"),
    platforms=["Linux", "MacOS"],
    packages=find_packages(),
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=requires,
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        "console_scripts": ["request-ssh-access = request_ssh_access.__main__:main"]
    },
)
