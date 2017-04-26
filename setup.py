# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='cosmicrays',
    version='0.1.0',
    description='Project for obtaining statistical information on cosmic rays incidence in FITS images',
    long_description=readme,
    author='Germán Schnyder',
    author_email='gschnyder@gmail.com',
    url='https://github.com/gschnyder/cosmicrays',
    license=license,
    packages=find_packages(exclude=['docs', 'tests']),
    entry_points={
        'console_scripts': [
            'cr_count=scripts:main',
        ]
    }
)
