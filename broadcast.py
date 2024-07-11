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
# File NOT need in production!!!

# This LfK (locations + JSON) distribution is meant to be a part of a system
# with a central Kafka topic that updates the network
# when relevant operations take place.

# This file can be used to mimic the kind of messagesn in said central topic.

# The schema for the central topic (and therefore messages sent to it)
# must contain the following fields (at least):
#   - event_type: (str) describes the type of event,
#   - path: (str) path to resource,
#   - operation_metadata: (obj) metadata w. transcription settings
#
# For transcription messages, the metadata field must contain:
#   - filename: (str) target name for OUTPUT file
#       (only name - no extension)
#   - transcription_approach: (str) 'simple' | 'segmentation' | 'diarisation'
#       (preferred transcription approach)
#   - model_size: (str) 'tiny' | 'base' | 'small' | 'medium' | 'large'
#       (size of model to use)
#   - final: (str) 'yes' | 'no'
#       (trigger – no transcription produced if not present or negated)
#   - timestamps: (str) 'yes | 'no'
#       (whether to add timestamps to transcriptions)


# ..................
# TOP-LEVEL IMPORTS
# ...
# Python
import os
import time
import mimetypes
from dotenv import load_dotenv

# Kafka core
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

# Kafka helpers and utils
from config import config, sr_config
from schemas import json_schemas
from config_folders import SOURCE_FOLDER
from utils.classes import KafkaEventBroadcast
from utils.conversions import event_to_event_dict


# ..................
# FAUX SYSTEM EVENTS
# ...
def faux_events(path_to_folder, topic):
    ''' Creates faux event updates to send to central messaging topic

        Arguments:
        - path_to_folder: (str) path to folder containing test audios
        - topic: (str) name of topic to produce messages to

        Outputs:
        - A call to a Kafka producer (per file in list or source audio)
    '''

    # Imports specific to this f(x)
    import random

    # System-wide event type for transcriptions
    event_type = 'audio'

    # Possible values for metadata
    model_size = ['tiny', 'base']  # , 'small', 'medium', 'large']
    transcription_approach = ['simple', 'segmentation']  # , 'diarisation']
    timestamps = ['yes', 'no']
    final = 'yes'

    # External audio urls
    # Leave empty if testing with internal audios (place in './sources')
    # For AWS, use S3 URI
    # No other services are currently supported
    base_url = f's3://{os.getenv("AWS_BUCKET_NAME")}'
    target_audios = ['33s.wav', 'mp3_audio.mp3']

    # Test using external resources if target_audios has entries
    if os.getenv("CLIENT_NAME") != 'internal' and len(target_audios) > 0:
        for file in target_audios:
            path = f'{base_url}/{file}'
            target_filename = file.split('.')[0]
            operation_metadata = {'filename': target_filename,
                                  'transcription_approach': random.choice(transcription_approach),
                                  'model_size': random.choice(model_size),
                                  'final': final,
                                  'timestamps': random.choice(timestamps)}
            produce(topic, event_type, path, operation_metadata)

    # Else, loop over files in source folder, send message with random metadata
    elif os.getenv("CLIENT_NAME") == 'internal':
        for file in os.listdir(path_to_folder):

            # In case folder has non-audio files, get file type
            try:
                file_type = mimetypes.guess_type(f'{path_to_folder}/{file}')[0].split('/')[0]
            except Exception as e:
                file_type = f'error determining file type: {e}'

            # Trigger message if type is audio
            if file_type == 'audio':
                path = f'{path_to_folder}/{file}'.replace('//', '/')
                target_filename = file.split('.')[0]
                operation_metadata = {'filename': target_filename,
                                      'transcription_approach': random.choice(transcription_approach),
                                      'model_size': random.choice(model_size),
                                      'final': final,
                                      'timestamps': random.choice(timestamps)}
                produce(topic, event_type, path, operation_metadata)
            else:
                pass

    else:
        print('No test messages created.\
            \nPlease select client name and ensure settings match selection.')


# ..................
# KAFKA PRODUCER
# ...
def delivery_report(err, event):
    ''' Callback function to communicate success or failure
    '''
    if err is not None:
        print(f'Delivery failed on reading for {event.key()}: {err}')
    else:
        print(f'Message produced to {event.topic()}')


def produce(topic, event_type, path, operation_metadata):
    ''' Messages event information to central topic

        Arguments:
        - topic: (str) name of topic to produce messages to
        - event_type: (str) the type of event triggering message
        - path: (str) the path to the associated resource
        - operation_metadata: (obj) metadata w. transcription settings

        Outputs
        - A message sent to a Kafka topic
    '''

    # Connect to schema registry
    try:
        schema_registry_client = SchemaRegistryClient(sr_config)
        schema_str = json_schemas.event_broadcast_str
        serializer = JSONSerializer(schema_str, schema_registry_client, to_dict=event_to_event_dict)
    except Exception as e:
        print(f'Unable to connect to schema registry or set schema: {e}')

    # Messaging
    try:
        # Announce message
        print('Sending test event to central topic')

        # Create message
        event_out = KafkaEventBroadcast(event_type, path, operation_metadata, round(time.time()*1000))
        message = serializer(event_out, SerializationContext(topic, MessageField.VALUE))

        # Produce message
        producer = Producer(config)
        producer.produce(topic=topic, key=event_type, value=message, on_delivery=delivery_report)

        # Flush producer
        producer.flush()
    except Exception as e:
        print(f'Producer error.\nPath: {path}.\nError: {e}')


# ..................
# NAME-MAIN
# ...
if __name__ == '__main__':

    # Load environmental variables
    load_dotenv()

    # Run loop of faux events that call producer
    faux_events(SOURCE_FOLDER, os.getenv('CENTRAL_TOPIC'))
