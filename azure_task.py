import os, os.path, sys

import datetime
import numpy
import argparse
import configparser

from astropy.utils.iers import iers

from common import helpers
from lib import calc_pos
import azure.storage.blob as azureblob
from azure.storage.table import TableService, Entity, TableBatch
from lib import crutils

import logging

config = configparser.ConfigParser()
config.read('configuration.cfg')

_LOGS_ACCOUNT_NAME = config.get(option='logsaccountname', section='Logs')
_LOGS_ACCOUNT_KEY = config.get(option='logsaccountkey', section='Logs')
__SAVE_CR_SEPARATELY_ = False


def upload_output_to_blob():
    blob_client = azureblob.BlockBlobService(account_name=args.storageaccount, sas_token=args.sastoken)
    output_file_path = os.path.realpath(output_file)
    print('Uploading file {} to container [{}]...'.format(output_file_path, args.storagecontainer))
    blob_client.create_blob_from_path(args.storagecontainer, output_file, output_file_path)


if __name__ == '__main__':

    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    try:
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

        iers.conf.auto_download = False
        iers.conf.auto_max_age = None

        input_file = os.path.realpath(args.filepath)
        output_file = '{}_OUTPUT{}'.format(
            os.path.splitext(args.filepath)[0],
            os.path.splitext(args.filepath)[1])

        logging.basicConfig(filename=output_file, filemode='w+', level=logging.INFO)

        logging.info('Started processing at {} '.format(datetime.datetime.now().replace(microsecond=0)))

        data_ext = helpers.extension_from_filename(input_file)
        pos_ext = helpers.pos_ext_from_data_ext(data_ext)
        pos_input_file = input_file.replace(data_ext, pos_ext)

        img = crutils.load(input_file, pos_input_file)

        logging.info('Loaded image {} for instrument {}'.format(img.file_name, img.instrument.NAME))

        _, cr_pixels = crutils.clean_cr(img.data, None, 2)

        logging.info('Got {} cr pixels'.format(numpy.sum(cr_pixels)))

        crs = crutils.reduce_cr(cr_pixels, img.exposition_duration)

        logging.info('Got {} cosmic rays'.format(len(crs)))

        long, lat, height = calc_pos.calc_pos(img)

        logging.info('Output: CR {}, Lat {}, Long {}, Height {}'.format(len(crs), long, lat, height))

        logging.info('Finished processing at {} '.format(datetime.datetime.now().replace(microsecond=0)))

        table_service = TableService(account_name=_LOGS_ACCOUNT_NAME,
                                     account_key=_LOGS_ACCOUNT_KEY)

        task = Entity()
        task.PartitionKey = img.instrument.NAME
        task.RowKey = img.observation_set
        task.cr_count = len(crs)
        task.latitude = str(lat)
        task.longitude = str(long)
        task.height = str(height)
        task.image_type = img.file_type
        task.observation_date = str(img.observation_date)
        task.observation_start_time = str(img.observation_start_time)
        task.exposition_duration = str(img.exposition_duration)
        task.proposal_id = str(img.proposal_id)

        task.position_angle = str(img.position_angle)
        task.right_ascension = str(img.right_ascension)
        task.declination = str(img.declination)

        if img.aperture is not None:
            task.aperture = str(img.aperture)
            task.ecliptic_lon = str(img.ecliptic_lon)
            task.ecliptic_lat = str(img.ecliptic_lat)
            task.galactic_lon = str(img.galactic_lon)
            task.galactic_lat = str(img.galactic_lat)

        table_service.insert_or_replace_entity('imagestable', task)

        # for chunk in chunks(crs, 100):
        #    batch = TableBatch()
        if __SAVE_CR_SEPARATELY_:
            logging.info('Done inserting image at {} '.format(datetime.datetime.now().replace(microsecond=0)))
            logging.info('Started cr individual inserts')
            for cr in crs:
                cr_task = {'PartitionKey': img.observation_set, 'RowKey': cr.label}

                for prop in cr:
                    cr_task[prop] = str(cr[prop])

                table_service.insert_or_replace_entity(cr_task)
                # batch.insert_or_replace_entity(cr_task)
                # table_service.commit_batch('crtable', batch)

        logging.info('Done with everything at {} '.format(datetime.datetime.now().replace(microsecond=0)))
        upload_output_to_blob()

    except Exception as e:
        logging.exception('Unexpected error')
        upload_output_to_blob()
        raise

