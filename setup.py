# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import cnmc_client

INSTALL_REQUIRES = ['Authlib', 'Munch', 'Marshmallow']

setup(
    name='CNMC Client',
    description='Python client desired to interact with the CNMC API',
    version=cnmc_client.__version__,
    url='https://www.gisce.net',
    author='Xavi Torelló',
    author_email='xtorello@gisce.net',
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
