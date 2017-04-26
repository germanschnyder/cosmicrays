# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='cosmicrays',
    version='0.0.1',
    description='Project for obtaining statistical information on cosmic rays incidence',
    long_description=readme,
    author='Germán Schnyder',
    author_email='german.schnyder@fing.edu.uy',
    url='https://github.com/germanschnyder/cosmicrays',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)