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
# File contains helper functions to convert stuff in various ways.
# Typical conversions:
# - Kafka operations (dictionaries <-> object)
# - Audio manipulations.


# ---------------------
# FOR EVENT BROADCASTING
# ...
def event_to_event_dict(eventio, ctx):
    ''' Converts faux operations data to dictionary
        Used by the test producer to mimic event broadcast messages
    '''

    return {
        'event_type': eventio.event_type,
        'path': eventio.path,
        'operation_metadata': eventio.operation_metadata,
        'timestamp': eventio.timestamp
        }


def event_dict_to_audio_loc(dict, ctx):
    ''' Converts event dictionary to audio location object
        Used by the audio consumer to retrieve audio locations from topic
    '''

    from utils.classes import KafkaEventBroadcast

    return KafkaEventBroadcast(
        dict['event_type'],
        dict['path'],
        dict['operation_metadata'],
        dict['timestamp']
        )


# ---------------------
# FOR TRANSCRIPTION
# ...
def transcription_to_dict(transcription, ctx):
    ''' Converts audio object to dictionary
        Used by transcriptions producer to send transcription outputs
    '''

    return {
        'path_to_transcription': transcription.path_to_transcription,
        'operation_metadata': transcription.operation_metadata,
        'content': transcription.content,
        'timestamp': transcription.timestamp
        }


def dict_to_transcription(dict, ctx):
    ''' Converts dictionary to string object
        Used by transcriptions consumer to retrieve transcriptions from topic
    '''

    from utils.classes import KafkaTranscription

    return KafkaTranscription(
        dict['path_to_transcription'],
        dict['operation_metadata'],
        dict['content'],
        dict['timestamp']
        )


# ---------------------
# FOR AUDIO MANIPULATION
# ...
def any_format_to_wav(path_to_audio):
    ''' Converts audio in any format to .wav
        NB! FFmpeg must be installed on system.

        Arguments:
        - path_to_audio: (str) the path to where audio is located.

        Outputs:
        - buffer: (bytes buffer) a buffer with the audio bytes
    '''

    import io
    from pydub import AudioSegment

    try:
        buffer = io.BytesIO()
        audio = AudioSegment.from_file(path_to_audio)
        audio.export(buffer, format='wav')
    except Exception as e:
        print(f'Error converting audio file to .wav format: {e}')

    return buffer
