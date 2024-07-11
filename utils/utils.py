'''
LOKAL for Kafka (LfK), v1. May 2024.
@author: Dr J.

Except for absolutely necessary classes,
LfK tries to stick to a functional programming paradigm.
Any classes must be justified exceptionally well.

Copyright (c) 2024 Jose A Bolanos / Polyzentrik Tmi.
SPDX-License-Identifier: Apache-2.0.

'''

# ..................
# FILE SUMMARY
# ...
# File contains helper functions, mainly for audio retrieval.


# ..................
# INTERNAL RETRIEVERS (no credentials needed)
# ...
def internal_retrieve(source_path, destination_path):
    ''' Retrieves an audio from an internal location not requiring auth

        Arguments:
        - source_path: (str) path to original audio
        - destination_path: (str) path to save audio to

        Outputs:
        - ONE audio saved to local transcriptions hub
            (for easier usage and manipulation during transcriptions)

    '''

    # Function imports
    import shutil

    # Copy into destination folder
    try:
        shutil.copyfile(source_path, destination_path)
        print(f'Retrieved! Find local copy at: {destination_path}')
    except Exception as e:
        print(f'Error with internal_retrieve f(x): {e}')


# ..................
# EXTERNAL RETRIEVERS (credentials needed)
# Currently supported: AWS S3
# ...
def s3_path_handler(path):
    ''' Takes an S3 path and breaks it into bucket and resource

        Arguments:
        - path: (str) the path to some S3 resource

        Outputs:
        - bucket_name: (str) the AWS bucket where the resource is
        - resource_location: (str) the location of resource in bucket

    '''
    # Split an S3 path into bucket name and resource
    path = path.replace('s3://', '').split('/')
    bucket_name = path.pop(0)
    resource_location = '/'.join(path)

    # Return the said bucket name and resource
    return bucket_name, resource_location


def external_retrieve(source_path, destination_path, client_name, credentials):
    ''' Retrieves an audio from an external location

        Arguments:
        - source_path: (str) url where audio is originally located
        - destination_path: (str) local path to save audio to
        - client_name: (str) name of the service used to store audios
        - credentials: (list) list with access credentials

        Outputs:
        - ONE audio saved to transcriptions hub
            (for easier usage and manipulation during transcriptions)

    '''

    try:
        match client_name:
            case 'aws':

                # Announce retrieval
                print('Retrieving audio from AWS (S3)')

                # Import Boto3 to connect to AWS
                import boto3

                # Break credentials spring into necessary components
                aws_region, aws_id, aws_key = credentials

                # Break path into bucket and resource name
                bucket_name, resource_location = s3_path_handler(source_path)

                # Open session
                ses = boto3.Session(
                    aws_access_key_id=aws_id,
                    aws_secret_access_key=aws_key,
                    region_name=aws_region
                    )
                s3 = ses.resource('s3')

                # Download audio
                s3.Bucket(bucket_name).download_file(resource_location, destination_path)

                # Declare victory
                print(f'Retrieved. Local copy at: {destination_path}')

            case _:
                print('Selected client not available. Check .env')
    except Exception as e:
        print(f'Error downloading external resource: {e}')
