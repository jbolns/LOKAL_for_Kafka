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
# File contains the Kafka consumer that reads central topic and
# retrieves and places any audio into async transcriptions folder


# ..................
# TOP-LEVEL IMPORTS
# ...
# Python
import os
import threading
from dotenv import load_dotenv

# Kafka core
from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer

# Kafka helpers and utils
from schemas import json_schemas
from config import config
from utils.conversions import event_dict_to_audio_loc

# LOKAL transcriptions
from utils.retrieve import audio_retriever


# ..................
# KAFKA CONSUMER
# ...
# Consumer configs
def set_consumer_configs():
    ''' Sets configs specific to this consumer
    '''

    config['group.id'] = 'audios_group'
    config['auto.offset.reset'] = 'earliest'


# Main consumer function
def consume(topic):
    ''' Consumes messages from central topic and processes them.

        Arguments:
        - topic: (str) name of topic from which to consume

        Outputs:
        - If event is audio, a call to a retrieval function,
            which saves audio to async transcriptions folder
    '''

    # Set consumer configs
    set_consumer_configs()

    # Set schema
    try:
        schema_str = json_schemas.event_broadcast_str
        deserializer = JSONDeserializer(schema_str, from_dict=event_dict_to_audio_loc)
    except Exception as e:
        print(f'Unable set schema: {e}')

    # Consume like a degenerate
    consumer = Consumer(config)
    consumer.subscribe([topic])
    print('Audio consumer is running.')

    while True:
        try:
            event = consumer.poll(1.0)

            if event is None:
                continue

            audio_in = deserializer(event.value(), SerializationContext(topic, MessageField.VALUE))

            if audio_in is not None:

                # Announce new message
                print(f'\n------\nNew event. Type: {audio_in.event_type}')

                # If audio, retrieve and place in async folder
                if audio_in.event_type == 'audio':
                    try:
                        retrieval_thread = threading.Thread(
                            target=audio_retriever(
                                audio_in.path,
                                audio_in.operation_metadata),
                            daemon=True)
                        retrieval_thread.start()
                    except Exception as e:
                        print(f'Failed to retrieve audio.\nError: {e}')
                else:
                    print('Event not transcribable.')

                # Announce wait for new message
                print('\n\nWaiting for next message.\n------')
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'Error with message – will continue to next message.\
                \nError is: {e}')

    consumer.close()


# ..................
# NAME-MAIN
# ...
if __name__ == '__main__':

    # Load environment variables
    load_dotenv()

    # Start the consumer
    consume(os.getenv('CENTRAL_TOPIC'))
