#!/usr/bin/env python
import argparse
import os
import sys
import logging
import csv
from collections import OrderedDict

from common.image import Image
from lib.crstats import calculate

'''
Use like:

ls *_raw.fits | parallel -I {} cr_count --filepath={}

requires GNU parallel
'''

from common import helpers
from lib import crutils, calc_pos


def main():
    logging.basicConfig(level=logging.ERROR)

    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', required=True,
                        help='file to parse')
    parser.add_argument('--write-headers', required=False,
                        help='write headers in the output')

    args = parser.parse_args()
    input_file = os.path.realpath(args.filepath)
    data_ext = helpers.extension_from_filename(input_file)
    pos_ext = helpers.pos_ext_from_data_ext(data_ext)
    pos_input_file = input_file.replace(data_ext, pos_ext)
    img = crutils.load(input_file, pos_input_file)
    _, cr_pixels = crutils.clean_cr(img.data, mask=None, iterations=2, gain=img.gain)
    crs, normalized_img = crutils.reduce_cr(cr_pixels, img.exposition_duration)
    long, lat, height = calc_pos.calc_pos(img)
    stats = calculate(crs, normalized_img)
    entity = output(img, crs, lat, long, height, stats, 0)
    logging.debug(entity)

    writer = csv.writer(sys.stdout)
    if args.write_headers:
        writer.writerow(entity)
    writer.writerow(entity.values())


def output(img: Image, crs, lat, long, height, stats, ptime):

    task = OrderedDict()
    task["PartitionKey"] = img.instrument.NAME
    task["RowKey"] = img.observation_set
    task["processing_time"] = ptime
    task["cr_count"] = len(crs)
    task["latitude"] = str(lat)
    task["longitude"] = str(long)
    task["height"] = str(height)
    task["image_type"] = img.file_type
    task["observation_date"] = str(img.observation_date)
    task["observation_start_time"] = str(img.observation_start_time)
    task["equinox"] = str(img.equinox)
    task["exposition_duration"] = str(img.exposition_duration)
    task["gain"] = str(img.gain)
    task["proposal_id"] = str(img.proposal_id)
    task["position_angle"] = str(img.position_angle)
    task["right_ascension"] = str(img.right_ascension)
    task["right_ascension_target"] = str(img.right_ascension_target)
    task["declination"] = str(img.declination)
    task["declination_target"] = str(img.declination_target)

    if img.aperture is not None:
        task["aperture"] = str(img.aperture)
        task["ecliptic_lon"] = str(img.ecliptic_lon)
        task["ecliptic_lat"] = str(img.ecliptic_lat)
        task["galactic_lon"] = str(img.galactic_lon)
        task["galactic_lat"] = str(img.galactic_lat)

    task["moon_angle"] = str(img.moon_angle)
    task["sun_angle"] = str(img.sun_angle)
    task["sun_altitude"] = str(img.sun_altitude)
    task["wcs_axes"] = img.wcs_axes

    for idx in range(1, img.wcs_axes + 1):
        task['wcs_crpix_%d' % idx] = str(img.wcs_crpix(idx))
        task['wcs_crval_%d' % idx] = str(img.wcs_crval(idx))
        task['wcs_ctype_%d' % idx] = str(img.wcs_ctype(idx))
        for part in [1, 2]:
            task['wcs_cd_%d_%d' % (idx, part)] = str(img.wcs_cd(idx, part))
        task['wcs_ltv_%d' % idx] = str(img.wcs_ltv(idx))
        task['wcs_ltm_%d' % idx] = str(img.wcs_ltm(idx))

    task["wcs_pa_aper"] = str(img.wcs_pa_aper)
    task["wcs_va_factor"] = str(img.wcs_va_factor)
    task["wcs_orientation"] = str(img.wcs_orientation)
    task["wcs_ra_aperture"] = str(img.wcs_ra_aperture)
    task["wcs_dec_aperture"] = str(img.wcs_dec_aperture)

    # Add stats
    for i, (key, value) in enumerate(stats.iteritems()):
        task['stat_%s' % key] = str(value)

    task['naxis'] = img.naxis
    for i in range(1, img.naxis + 1):
        task['naxis%d' % i] = img.naxis_i(i)

    task['binaxis1'] = img.binaxis1
    task['binaxis2'] = img.binaxis2

    return task
