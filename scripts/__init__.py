#!/usr/bin/env python
import argparse
import os
import sys
import logging

'''
Use like:

ls *_raw.fits | xargs -I {} cr_count --filepath={}
'''

from common import helpers
from lib import crutils, calc_pos


def main():
    logging.basicConfig(level=logging.ERROR)

    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', required=True,
                        help='file to parse')

    args = parser.parse_args()
    input_file = os.path.realpath(args.filepath)
    data_ext = helpers.extension_from_filename(input_file)
    pos_ext = helpers.pos_ext_from_data_ext(data_ext)
    pos_input_file = input_file.replace(data_ext, pos_ext)
    img = crutils.load(input_file, pos_input_file)
    _, cr_pixels = crutils.clean_cr(img.data, None, 2)
    crs = crutils.reduce_cr(cr_pixels, img.exposition_duration)
    long, lat, height = calc_pos.calc_pos(img)
    sys.stdout.write("file: {0}\tcrs: {1:6d}\tlon: {2:.4f}\tlat: {3:.4f}\theight: {4:.4f}\n".format(img.file_name, len(crs), long, lat, height))
