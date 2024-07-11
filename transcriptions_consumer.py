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
# File consumes messages from final transcriptions (output) topic,
# saving transcription results to its final intended destination.

# ..................
# TOP-LEVEL IMPORTS
# ...
# Python
import os
from dotenv import load_dotenv

# Kafka core
from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer

# Kafka helpers and utils
from config import config
from config_folders import OUTPUT_FOLDER
from schemas import json_schemas
from utils.conversions import dict_to_transcription


# ..................
# KAFKA CONSUMER
# ...
# Consumer configs
def set_consumer_configs():
    ''' Sets configs specific to consumer
    '''
    config['group.id'] = 'transcriptions_group'
    config['auto.offset.reset'] = 'earliest'


# Main consumer function
def consume(topic, OUTPUT_FOLDER):
    ''' Consumes messages and processes them.

        Arguments:
        - topic: (str) name of topic to consume from

        Outputs:
        - ONE .txt file with contents of the transcription received in message
    '''

    # Set consumer configs
    set_consumer_configs()

    # Set schema
    try:
        schema_str = json_schemas.transcription_str
        deserializer = JSONDeserializer(schema_str, from_dict=dict_to_transcription)
    except Exception as e:
        print(f'Unable set schema: {e}')

    # Consume like a degenerate
    consumer = Consumer(config)
    consumer.subscribe([topic])
    print('Transcriptions consumer is running.')

    while True:
        try:
            event = consumer.poll(1.0)

            if event is None:
                continue

            transcription_in = deserializer(event.value(), SerializationContext(topic, MessageField.VALUE))

            if transcription_in is not None:

                # Announce new message
                print(f'\n------\nNew transcription available.\
                    \nAvailable at: {transcription_in.path_to_transcription}.\
                    \nCopying to: {OUTPUT_FOLDER}')

                # Write to file
                try:
                    filename = transcription_in.operation_metadata['filename']
                    with open(f'{OUTPUT_FOLDER}/{filename}.txt', 'w') as f:
                        f.write(transcription_in.content)
                        f.close
                except Exception as e:
                    print(f'Failed to consumer transcription.\nError: {e}')

                # Celebrate
                print('Success')
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'There was an error with this message: {e}.\
                \nConsumer will continue to next message.')

    consumer.close()


# ..................
# NAME-MAIN
# ...
if __name__ == '__main__':

    # Load environment
    load_dotenv()

    # Run consumer
    consume(os.getenv('FINAL_TRANSCRIPTIONS_TOPIC'), OUTPUT_FOLDER)
