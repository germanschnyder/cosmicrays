import os.path
import datetime
import numpy
import argparse
import logging
import timeit
from astropy.utils.iers import iers
from common import helpers
from db import azure
from lib import calc_pos, crutils, crstats


if __name__ == '__main__':

    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]


    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', required=True,
                        help='The path to the text file to process. The path'
                             'may include a compute node\'s environment'
                             'variables, such as'
                             '$AZ_BATCH_NODE_SHARED_DIR/filename.txt')
    parser.add_argument('--storageaccount', required=True,
                        help='The name the Azure Storage account that owns the'
                             'blob storage container to which to upload'
                             'results.')
    parser.add_argument('--storagecontainer', required=True,
                        help='The Azure Blob storage container to which to'
                             'upload results.')
    parser.add_argument('--sastoken', required=True,
                        help='The SAS token providing write access to the'
                             'Storage container.')
    args = parser.parse_args()
    input_file = os.path.realpath(args.filepath)
    output_file = '{}_OUTPUT{}.txt'.format(
        os.path.splitext(args.filepath)[0],
        os.path.splitext(args.filepath)[1])

    try:
        logging.basicConfig(filename=output_file, filemode='w+', level=logging.INFO)

        logging.info('Started processing at {} '.format(datetime.datetime.now().replace(microsecond=0)))

        tic = timeit.default_timer()

        data_ext = helpers.extension_from_filename(input_file)
        pos_ext = helpers.pos_ext_from_data_ext(data_ext)
        pos_input_file = input_file.replace(data_ext, pos_ext)

        img = crutils.load(input_file, pos_input_file)

        logging.info('Loaded image {} for instrument {}'.format(img.file_name, img.instrument.NAME))

        _, cr_pixels = crutils.clean_cr(img.data, mask=None, iterations=2, gain=img.gain)

        logging.info('Got {} cr pixels'.format(numpy.sum(cr_pixels)))

        crs, normalized_img = crutils.reduce_cr(cr_pixels, img.exposition_duration)

        logging.info('Got {} cosmic rays'.format(len(crs)))

        long, lat, height = calc_pos.calc_pos(img)

        logging.info('Output: CR {}, Lat {}, Long {}, Height {}'.format(len(crs), long, lat, height))

        stats = crstats.calculate(crs, normalized_img)

        logging.info('Stats: {}'.format(stats))

        toc = timeit.default_timer()

        logging.info('Finished processing at {} '.format(datetime.datetime.now().replace(microsecond=0)))

        azure.save_image(img, crs, lat, long, height, stats, toc - tic)

        logging.info('Done with everything at {} '.format(datetime.datetime.now().replace(microsecond=0)))

        azure.save_output(args, output_file)

    except Exception as e:
        logging.exception('Unexpected error')
        azure.save_output(args, output_file)
        raise

