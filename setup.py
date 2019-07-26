#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
import os

import version_incrementor


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name="request-ssh-access",
    author="HRMC Platform Security",
    author_email="platsec.monitor@digital.hmrc.gov.uk",
    version=version_incrementor.prepare_release(major=0),
    description="Helper utility to create Vault-signed SSH certificates",
    url="https://github.com/hmrc/request-ssh-access/",
    long_description=read("README.md"),
    platforms=["Linux", "MacOS"],
    packages=find_packages(),
    install_requires=["requests>=2.20.0"],
    entry_points={
        "console_scripts": ["request-ssh-access = request_ssh_access.__main__:main"]
    },
)
