# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

if not sys.version_info[0] == 3:
    sys.exit("Sorry, Python 2 is not supported (yet)")

setup(
    name='cosmicrays',
    version='0.4.0',
    description='Project for obtaining statistical information on cosmic rays incidence in FITS images',
    long_description=readme,
    author='Germán Schnyder',
    author_email='gschnyder@gmail.com',
    url='https://github.com/germanschnyder/cosmicrays',
    license=license,
    packages=find_packages(exclude=['docs', 'tests']),
    entry_points={
        'console_scripts': [
            'cr_count=scripts:main',
        ]
    },
    install_requires=[
        "numpy",
        "scipy",
        "scikit-image",
        "astropy",
        "argparse"
    ]
)
