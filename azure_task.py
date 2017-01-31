import os, os.path, sys

import numpy
import argparse
import configparser
from lib import calc_pos
import azure.storage.blob as azureblob
from azure.storage.table import TableService, Entity
from lib import crutils

import logging


config = configparser.ConfigParser()
config.read('configuration.cfg')

_LOGS_ACCOUNT_NAME = config.get(option='logsaccountname', section='Logs')
_LOGS_ACCOUNT_KEY = config.get(option='logsaccountkey', section='Logs')


if __name__ == '__main__':

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

        input_file = os.path.realpath(args.filepath)
        output_file = '{}_OUTPUT{}'.format(
            os.path.splitext(args.filepath)[0],
            os.path.splitext(args.filepath)[1])

        logging.basicConfig(filename=output_file, filemode='w+', level=logging.DEBUG)

        img = crutils.load(input_file)

        _, cr_pixels = crutils.clean_cr(img.data, None, 2)

        logging.info('Got {} cr pixels'.format(numpy.sum(cr_pixels)))

        crs = crutils.reduce_cr(cr_pixels, img.exposition_duration)

        logging.info('Got {} cosmic rays'.format(len(crs)))

        LONGITUDE, LATITUDE, HEIGHT = calc_pos.calc_pos(input_file.replace('raw', 'spt'), input_file)

        logging.info('Output: CR {}, Lat {}, Long {}, Height{}'.format(len(crs), LONGITUDE, LATITUDE, HEIGHT))

        table_service = TableService(account_name=_LOGS_ACCOUNT_NAME,
                                     account_key=_LOGS_ACCOUNT_KEY)

        task = Entity()
        task.PartitionKey = img.instrument
        task.RowKey = img.observation_set
        task.cr_count = len(crs)
        task.latitude = str(LATITUDE)
        task.longitude = str(LONGITUDE)
        task.height = str(HEIGHT)
        task.image_type = img.file_type
        task.observation_date = str(img.observation_date)
        task.observation_start_time = str(img.observation_start_time)
        task.exposition_duration = str(img.exposition_duration)

        table_service.insert_or_replace_entity('imagestable', task)

        for cr in crs:
            cr_task = {'PartitionKey': img.observation_set, 'RowKey': cr.label}

            for prop in cr:
                cr_task[prop] = str(cr[prop])

            table_service.insert_or_replace_entity('crtable', cr_task)

    except Exception as e:
        logging.exception('Unexpected error')

    # Create the blob client using the container's SAS token.
    # This allows us to create a client that provides write
    # access only to the container.
    blob_client = azureblob.BlockBlobService(account_name=args.storageaccount, sas_token=args.sastoken)

    output_file_path = os.path.realpath(output_file)

    print('Uploading file {} to container [{}]...'.format(output_file_path, args.storagecontainer))

    blob_client.create_blob_from_path(args.storagecontainer, output_file, output_file_path)
