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
# File contains classes used to build Kafka objects.


# ..................
# KAFKA OBJECTS
# ...
class KafkaEventBroadcast(object):
    ''' Takes an audio and makes an audio instance that can travel as message

        Arguments:
        - event_type: (str) type of event being broadcasted
        - path: (str) path to source resource triggering the broadcast
        - operation_metadata: (obj) metadata w. transcription settings
        - timestamp: (str) time of event
    '''

    def __init__(self, event_type, path, operation_metadata, timestamp):

        self.event_type = event_type
        self.path = path
        self.operation_metadata = operation_metadata
        self.timestamp = timestamp


class KafkaTranscription(object):
    ''' Converts transcription output to instance that can travel as message

        Arguments:
        - path_to_transcription: (str) path to transcription
        - operation_metadata: (obj) metadata w. transcription settings
        - content: (str) contents of transcription file
        - timestamp: (str) time of message
    '''

    def __init__(self, path_to_transcription, operation_metadata, content, timestamp):

        self.path_to_transcription = path_to_transcription
        self.operation_metadata = operation_metadata
        self.content = content
        self.timestamp = timestamp
