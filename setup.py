# -*- coding: utf-8 -*-
import io
import re
from setuptools import setup, find_packages

with io.open('cnmc_client/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

INSTALL_REQUIRES = ['Authlib==0.14.3', 'oauth', 'Munch', 'Marshmallow']

setup(
    name='CNMCClient',
    description='Python client desired to interact with the CNMC API',
    version=version,
    url='https://www.gisce.net',
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    license='General Public Licence 3',
    provides=['cnmc_client'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6"
    ]
)
