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
# File sends messages with transcription outputs to final transcriptions topic


# ..................
# TOP-LEVEL IMPORTS
# ...
# Python
import os
import time
from dotenv import load_dotenv

# Kafka core
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

# Kafka helpers and utils
from config import config, sr_config
from schemas import json_schemas
from utils.classes import KafkaTranscription
from utils.conversions import transcription_to_dict


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


def produce(path_to_transcription, operation_metadata):
    ''' Produces a Kafka message when there is a transcription available

        Arguments:
        - path_to_transcription: (str) path to save transcription to
        - operation_metadata: (obj) metadata w. transcription settings

        Outputs:
        - ONE .txt file with contents of the transcription for the source audio
            (saved to local device)
    '''

    # Update user
    print('\nSending transcription')

    # Load environment & topic name
    load_dotenv()
    topic = os.getenv('FINAL_TRANSCRIPTIONS_TOPIC')

    # Connect to schema registry
    try:
        schema_registry_client = SchemaRegistryClient(sr_config)
        schema_str = json_schemas.transcription_str
        serializer = JSONSerializer(schema_str, schema_registry_client, to_dict=transcription_to_dict)
    except Exception as e:
        print(f'Unable to connect to schema registry or set schema: {e}')

    # Send message
    try:
        # Create message
        with open(path_to_transcription, 'r') as f:
            content = f.read()
            f.close

        transcription_out = KafkaTranscription(path_to_transcription, operation_metadata, content, round(time.time()*1000))
        message = serializer(transcription_out, SerializationContext(topic, MessageField.VALUE))

        # Reset configs
        # (If called by a consumer, remove unnecessary items)
        # (If triggered directly, removal will leave configs intact)
        producer_configs = {key: val for key, val in config.items() if key not in ['group.id', 'auto.offset.reset']}

        # Produce message
        producer = Producer(producer_configs)
        producer.produce(topic=topic, key=operation_metadata['transcription_approach'], value=message, on_delivery=delivery_report)

        # Flush producer
        producer.flush()
    except Exception as e:
        print(f'Producer unable to send {path_to_transcription}: {e}')


# ..................
# NAME-MAIN
# ...
if __name__ == '__main__':
    pass
