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


print(config.items())


def save_output(args, output_file):
    blob_client = azureblob.BlockBlobService(account_name=args.storageaccount, sas_token=args.sastoken)
    output_file_path = os.path.realpath(output_file)
    print('Uploading file {} to container [{}]...'.format(output_file_path, args.storagecontainer))
    blob_client.create_blob_from_path(args.storagecontainer, output_file, output_file_path)


def save_image(img: Image, crs, lat, long, height, stats, ptime):
    table_service = TableService(account_name=_LOGS_ACCOUNT_NAME,
                                 account_key=_LOGS_ACCOUNT_KEY)
    task = Entity()
    task.PartitionKey = img.instrument.NAME
    task.RowKey = img.observation_set
    task.processing_time = ptime
    task.cr_count = len(crs)
    task.latitude = str(lat)
    task.longitude = str(long)
    task.height = str(height)
    task.image_type = img.file_type
    task.observation_date = str(img.observation_date)
    task.observation_start_time = str(img.observation_start_time)
    task.equinox = str(img.equinox)
    task.exposition_duration = str(img.exposition_duration)
    task.gain = str(img.gain)
    task.proposal_id = str(img.proposal_id)
    task.position_angle = str(img.position_angle)
    task.right_ascension = str(img.right_ascension)
    task.right_ascension_target = str(img.right_ascension_target)
    task.declination = str(img.declination)
    task.declination_target = str(img.declination_target)

    if img.aperture is not None:
        task.aperture = str(img.aperture)
        task.ecliptic_lon = str(img.ecliptic_lon)
        task.ecliptic_lat = str(img.ecliptic_lat)
        task.galactic_lon = str(img.galactic_lon)
        task.galactic_lat = str(img.galactic_lat)

    task.moon_angle = str(img.moon_angle)
    task.sun_angle = str(img.sun_angle)
    task.sun_altitude = str(img.sun_altitude)
    task.wcs_axes = img.wcs_axes

    for idx in range(1, img.wcs_axes + 1):
        task['wcs_crpix_%d' % idx] = str(img.wcs_crpix(idx))
        task['wcs_crval_%d' % idx] = str(img.wcs_crval(idx))
        task['wcs_ctype_%d' % idx] = str(img.wcs_ctype(idx))
        for part in [1, 2]:
            task['wcs_cd_%d_%d' % (idx, part)] = str(img.wcs_cd(idx, part))
        task['wcs_ltv_%d' % idx] = str(img.wcs_ltv(idx))
        task['wcs_ltm_%d' % idx] = str(img.wcs_ltm(idx))

    task.wcs_pa_aper = str(img.wcs_pa_aper)
    task.wcs_va_factor = str(img.wcs_va_factor)
    task.wcs_orientation = str(img.wcs_orientation)
    task.wcs_ra_aperture = str(img.wcs_ra_aperture)
    task.wcs_dec_aperture = str(img.wcs_dec_aperture)

    # Add stats
    for key, value in stats.items():
        task['stat_%s' % key] = str(value)

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
