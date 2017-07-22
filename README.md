# Readme
master:

[![Build Status](https://travis-ci.org/germanschnyder/cosmicrays.svg?branch=master)](https://travis-ci.org/germanschnyder/cosmicrays) [![Coverage Status](https://coveralls.io/repos/github/germanschnyder/cosmicrays/badge.svg?branch=master)](https://coveralls.io/github/germanschnyder/cosmicrays?branch=master)

dev:

[![Build Status](https://travis-ci.org/germanschnyder/cosmicrays.svg?branch=dev)](https://travis-ci.org/germanschnyder/cosmicrays) [![Coverage Status](https://coveralls.io/repos/github/germanschnyder/cosmicrays/badge.svg?branch=dev)](https://coveralls.io/github/germanschnyder/cosmicrays?branch=dev)


Installing the bash util
------------------------
pip install -r requirements.txt
python setup.py install

Then, obtain a list of the files to be processed and trigger parallel jobs:

ls \*flt\* | parallel -j 2 cr_count --filepath {} > flt.out
