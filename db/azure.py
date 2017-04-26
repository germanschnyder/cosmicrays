import configparser
import logging
import datetime
import os

import azure.storage.blob as azureblob

from azure.storage.table import TableService, Entity, TableBatch

from common.image import Image

config = configparser.ConfigParser()
config.read('configuration.cfg')

_LOGS_ACCOUNT_NAME = config.get(option='logsaccountname', section='Logs')
_LOGS_ACCOUNT_KEY = config.get(option='logsaccountkey', section='Logs')
__SAVE_CR_SEPARATELY_ = False


def save_output(args, output_file):
    blob_client = azureblob.BlockBlobService(account_name=args.storageaccount, sas_token=args.sastoken)
    output_file_path = os.path.realpath(output_file)
    print('Uploading file {} to container [{}]...'.format(output_file_path, args.storagecontainer))
    blob_client.create_blob_from_path(args.storagecontainer, output_file, output_file_path)


def save_image(img: Image, crs, lat, long, height):
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
