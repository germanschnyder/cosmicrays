Installing the bash util
------------------------
pip install -r requirements.txt
python setup.py install

Then, obtain a list of the files to be processed and trigger parallel jobs:

ls *flt* | parallel -j 2 cr_count --filepath {} > flt.out
