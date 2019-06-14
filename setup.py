#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
import os


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
    install_requires=["requests"],
    entry_points={
        "console_scripts": ["request-ssh-access = request_ssh_access.__main__:main"]
    },
)
