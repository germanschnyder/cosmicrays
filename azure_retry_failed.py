# python_tutorial_client.py - Batch Python SDK tutorial sample
#
# Copyright (c) Microsoft Corporation
#
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import print_function
import datetime
import os
import sys
import time
import configparser
import logging

from azure.batch.models import TaskListOptions

from common import helpers
from common.instruments import ACS, WFC3, STIS, WFPC2, NICMOS

try:
    input = raw_input
except NameError:
    pass

import azure.storage.blob as azureblob

import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels

sys.path.append('.')
sys.path.append('..')
import common.helpers  # noqa

config = configparser.ConfigParser()
config.read('configuration.cfg')

# Update the Batch and Storage account credential strings below with the values
# unique to your accounts. These are used when constructing connection strings
# for the Batch and Storage client objects.
_BATCH_ACCOUNT_NAME = config.get(option='batchaccountname', section='Batch')
_BATCH_ACCOUNT_KEY = config.get(option='batchaccountkey', section='Batch')
_BATCH_ACCOUNT_URL = config.get(option='batchserviceurl', section='Batch')

_STORAGE_ACCOUNT_NAME = config.get(option='storageaccountname', section='Storage')
_STORAGE_ACCOUNT_KEY = config.get(option='storageaccountkey', section='Storage')

_POOL_ID = config.get(option='prefix', section='Pool')  # + str(int(round(time.time() * 1000)))
_POOL_NODE_COUNT = config.get(option='nodecount', section='Pool')
_POOL_VM_SIZE = config.get(option='vmsize', section='Pool')

_NODE_OS_PUBLISHER = config.get(option='publisher', section='Node')
_NODE_OS_OFFER = config.get(option='offer', section='Node')
_NODE_OS_SKU = config.get(option='sku', section='Node')


_CONTAINER = config.get(option='container', section='Job')
_FOLDER = config.get(option='folder', section='Job')

_JOB_ID = 'HubbleImagesJob_home10_german_schnyder_disco3_'


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def print_batch_exception(batch_exception):
    """
    Prints the contents of the specified Batch exception.

    :param batch_exception:
    """
    print('-------------------------------------------')
    print('Exception encountered:')
    if batch_exception.error and \
            batch_exception.error.message and \
            batch_exception.error.message.value:
        print(batch_exception.error.message.value)
        if batch_exception.error.values:
            print()
            for mesg in batch_exception.error.values:
                print('{}:\t{}'.format(mesg.key, mesg.value))
    print('-------------------------------------------')


def upload_file_to_container(block_blob_client, container_name, folder, file_path):
    """
    Uploads a local file to an Azure Blob storage container.

    :param block_blob_client: A blob service client.
    :type block_blob_client: `azure.storage.blob.BlockBlobService`
    :param str container_name: The name of the Azure Blob storage container.
    :param str folder: The local path to the folder.    
    :param str file_path: The local path to the file.
    :rtype: `azure.batch.models.ResourceFile`
    :return: A ResourceFile initialized with a SAS URL appropriate for Batch
    tasks.
    """
    blob_name = os.path.join(folder, os.path.basename(file_path))

    logging.info('Uploading file {} to container [{}]...'.format(file_path, container_name))

    block_blob_client.create_blob_from_path(container_name,
                                            blob_name,
                                            file_path)

    sas_token = block_blob_client.generate_blob_shared_access_signature(
        container_name,
        blob_name,
        permission=azureblob.BlobPermissions.READ,
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=480))

    sas_url = block_blob_client.make_blob_url(container_name,
                                              blob_name,
                                              sas_token=sas_token)

    return batchmodels.ResourceFile(file_path=blob_name,
                                    blob_source=sas_url)


def get_file_details(block_blob_client, container_name, file_name):
    logging.debug("Finding details for %s" % file_name)

    # raw
    sas_token = block_blob_client.generate_blob_shared_access_signature(
        container_name,
        file_name,
        permission=azureblob.BlobPermissions.READ,
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=480))

    sas_url = block_blob_client.make_blob_url(container_name,
                                              file_name,
                                              sas_token=sas_token)

    # pos
    data_ext = helpers.extension_from_filename(file_name)
    pos_ext = helpers.pos_ext_from_data_ext(data_ext)

    logging.debug("Details for files %s and %s" % (data_ext, pos_ext))

    pos_file_name = file_name.replace(data_ext, pos_ext)
    pos_sas_token = block_blob_client.generate_blob_shared_access_signature(
        container_name,
        pos_file_name,
        permission=azureblob.BlobPermissions.READ,
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=480))

    pos_sas_url = block_blob_client.make_blob_url(container_name,
                                                  pos_file_name,
                                                  sas_token=pos_sas_token)

    logging.debug('File details for {} and {}'.format(file_name, pos_file_name))

    return (
        batchmodels.ResourceFile(file_path=file_name, blob_source=sas_url),
        batchmodels.ResourceFile(file_path=pos_file_name, blob_source=pos_sas_url)
    )


def get_container_sas_token(block_blob_client,
                            container_name, blob_permissions):
    """
    Obtains a shared access signature granting the specified permissions to the
    container.

    :param block_blob_client: A blob service client.
    :type block_blob_client: `azure.storage.blob.BlockBlobService`
    :param str container_name: The name of the Azure Blob storage container.
    :param BlobPermissions blob_permissions:
    :rtype: str
    :return: A SAS token granting the specified permissions to the container.
    """
    # Obtain the SAS token for the container, setting the expiry time and
    # permissions. In this case, no start time is specified, so the shared
    # access signature becomes valid immediately.
    container_sas_token = \
        block_blob_client.generate_container_shared_access_signature(
            container_name,
            permission=blob_permissions,
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=480))

    return container_sas_token


def list_unfinished_job_tasks(batch_service_client, job_id, max_results):

    tasks = batch_service_client.task.list(job_id, task_list_options=TaskListOptions(
        max_results=max_results,
        filter='state eq \'active\''
    ))

    incomplete_tasks = [task for task in tasks if
                        task.state != batchmodels.TaskState.completed]

    for itask in incomplete_tasks:
        logging.info('Got task [{}]...'.format(itask))

    return incomplete_tasks


def create_job(batch_service_client, job_id, pool_id):
    """
    Creates a job with the specified ID, associated with the specified pool.

    :param batch_service_client: A Batch service client.
    :type batch_service_client: `azure.batch.BatchServiceClient`
    :param str job_id: The ID for the job.
    :param str pool_id: The ID for the pool.
    """
    logging.info('Creating job [{}]...'.format(job_id))

    job = batch.models.JobAddParameter(
        job_id,
        batch.models.PoolInformation(pool_id=pool_id),
        priority=-1)

    try:
        batch_service_client.job.add(job)
    except batchmodels.batch_error.BatchErrorException as err:
        print_batch_exception(err)
        raise


def add_tasks(batch_service_client, job_id, input_files,
              output_container_name, output_container_sas_token):
    """
    Adds a task for each input file in the collection to the specified job.

    :param batch_service_client: A Batch service client.
    :type batch_service_client: `azure.batch.BatchServiceClient`
    :param str job_id: The ID of the job to which to add the tasks.
    :param list input_files: A collection of input files. One task will be
     created for each input file.
    :param output_container_name: The ID of an Azure Blob storage container to
    which the tasks will upload their results.
    :param output_container_sas_token: A SAS token granting write access to
    the specified Azure Blob storage container.
    """

    logging.info('Adding {} tasks to job [{}]...'.format(len(input_files), job_id))

    tasks = list()
    tasked = 0
    for idx, (raw, spt) in enumerate(input_files):
        command = ['ls -l ' + raw.file_path,
                   'ls -l ' + spt.file_path,
                   'python3 $AZ_BATCH_NODE_SHARED_DIR/azure_task.py '
                   '--filepath {} --storageaccount {} '
                   '--storagecontainer {} --sastoken "{}"'.format(
                       raw.file_path,
                       _STORAGE_ACCOUNT_NAME,
                       output_container_name,
                       output_container_sas_token)]

        tasks.append(batch.models.TaskAddParameter(
            'topNtask{}'.format(idx),
            common.helpers.wrap_commands_in_shell('linux', command),
            resource_files=[raw, spt]
        )
        )

        if tasked == 99:
            batch_service_client.task.add_collection(job_id, tasks)
            logging.info("Just dispatched a batch")
            tasked = 0
            tasks.clear()
        else:
            tasked += 1

    batch_service_client.task.add_collection(job_id, tasks)
    logging.info("Just dispatched last batch of %d" % len(tasks))


def is_valid_extension(blob):
    valid_extensions_arr = [ACS.DATA_FILE_EXT, WFC3.DATA_FILE_EXT, STIS.DATA_FILE_EXT, WFPC2.DATA_FILE_EXT,
                            NICMOS.DATA_FILE_EXT]
    valid_extensions = ",".join([item for sublist in valid_extensions_arr for item in sublist])
    ext = helpers.extension_from_filename(blob.name)

    logging.debug("Testing file %s with extension %s to be in %s" % (blob.name, ext, valid_extensions))

    return ext in valid_extensions


if __name__ == '__main__':

    app_container_name = 'application'
    output_container_name = 'output'

    blob_client = azureblob.BlockBlobService(
        account_name=_STORAGE_ACCOUNT_NAME,
        account_key=_STORAGE_ACCOUNT_KEY)

    blobs = []
    marker = None
    container = _CONTAINER
    prefix = _FOLDER

    # while True:
    #     bbatch = blob_client.list_blobs(container_name=container, prefix=prefix, marker=marker, delimiter='/')
    #     blobs.extend(bbatch)
    #     if not bbatch.next_marker:
    #         break
    #     marker = bbatch.next_marker
    #
    # input_files = [
    #     get_file_details(blob_client, 'all', blob.name)
    #     for blob in blobs if is_valid_extension(blob)
    # ]
    #
    # output_container_sas_token = get_container_sas_token(
    #     blob_client,
    #     output_container_name,
    #     azureblob.BlobPermissions.WRITE)

    credentials = batchauth.SharedKeyCredentials(_BATCH_ACCOUNT_NAME,
                                                 _BATCH_ACCOUNT_KEY)

    batch_client = batch.BatchServiceClient(
        credentials,
        base_url=_BATCH_ACCOUNT_URL)

    unfinished_tasks = list_unfinished_job_tasks(batch_client, _JOB_ID, 10)

    print(unfinished_tasks[0])

    # try:
    #
    #     create_job(batch_client, _JOB_ID, _POOL_ID)
    #
    #     add_tasks(batch_client,
    #               _JOB_ID,
    #               input_files,
    #               output_container_name,
    #               output_container_sas_token)
    #
    # except Exception as e:
    #     logging.exception('Unexpected error')
