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


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    logging.basicConfig(level=logging.ERROR)

    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', required=True,
                        help='file to parse')

    parser.add_argument('--output-filename', required=False,
                        help='output filename')

    parser.add_argument('--write-headers', required=False, type=str2bool, nargs='?', default=False,
                        help='write headers in the output')

    parser.add_argument('--include-cr-list', required=False, type=str2bool, nargs='?', default=False,
                        help='write separate cr info in the output')

    parser.add_argument('--lacosmic-iterations', required=False, type=int, default=4,
                        help='number of iterations to run lacosmic algorithm')

    parser.add_argument('--lacosmic-gain', required=False, type=float,
                        help='gain to be applied to lacosmic algorithm')

    parser.add_argument('--lacosmic-readnoise', default=3, type=float)
    parser.add_argument('--lacosmic-sigclip', default=5.0, type=float)
    parser.add_argument('--lacosmic-sigfrac', default=0.3, type=float)
    parser.add_argument('--lacosmic-objlim', default=5.0, type=float)
    parser.add_argument('--lacosmic-satlevel', default=-1.0, type=float,
                        help='saturation level for lacosmic (use negative to skip)')

    args = parser.parse_args()

    input_file = os.path.realpath(args.filepath)
    data_ext = helpers.extension_from_filename(input_file)
    pos_ext = helpers.pos_ext_from_data_ext(data_ext)
    pos_input_file = input_file.replace(data_ext, pos_ext)
    img = crutils.load(input_file, pos_input_file)

    gain = img.gain
    if args.lacosmic_gain is not None:
        gain = args.lacosmic_gain

    _, cr_pixels = crutils.clean_cr(img.data,
                                    mask=None,
                                    iterations=args.lacosmic_iterations,
                                    gain=gain,
                                    readnoise=args.lacosmic_readnoise,
                                    sigclip=args.lacosmic_sigclip,
                                    sigfrac=args.lacosmic_sigfrac,
                                    objlim=args.lacosmic_objlim,
                                    satlevel=args.lacosmic_satlevel)

    crs, normalized_img = crutils.reduce_cr(cr_pixels, img.exposition_duration)
    long, lat, height = calc_pos.calc_pos(img)
    stats = calculate(crs, normalized_img)
    entity = output(img, crs, lat, long, height, stats, 0)
    logging.debug(entity)
    write_to_file = False
    if args.output_filename:
        write_to_file = True
        writer = csv.writer(open(args.output_filename, "w"))
    else:
        writer = csv.writer(sys.stdout)

    if args.write_headers:
        writer.writerow(entity)
    writer.writerow(entity.values())

    cr_info = output_crs(img.observation_set, crs)
    logging.debug(cr_info)

    if args.include_cr_list:
        if write_to_file:
            cr_writer = csv.writer(open(args.output_filename + "_cr_info", "w"))
        else:
            cr_writer = writer

        if args.write_headers:
            cr_writer.writerow(cr_info)
        cr_writer.writerow(cr_info.values())


def output_crs(observation_set, crs):
    for cr in crs:
        task = OrderedDict()
        task["PartitionKey"] = observation_set
        task["RowKey"] =  cr.label

        for prop in cr:
            task[prop] = str(cr[prop])

    return task


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
    for key, value in stats.items():
        task['stat_%s' % key] = str(value)

    task['naxis'] = img.naxis
    for i in range(1, img.naxis + 1):
        task['naxis%d' % i] = img.naxis_i(i)

    task['binaxis1'] = img.binaxis1
    task['binaxis2'] = img.binaxis2
    task['bunit'] = img.bunit

    return task
