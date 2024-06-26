'''
LOKAL for Kafka (LfK), v1. May 2024.
@author: Dr J.

Except for absolutely necessary classes, LfK tries to stick to a functional programming paradigm.
Any classes must be justified exceptionally well.

Copyright (c) 2024 Jose A Bolanos / Polyzentrik Tmi.
SPDX-License-Identifier: Apache-2.0.

'''

audio_str = """{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "audio",
    "description": "Audio segments",
    "type": "object",
    "properties": {
        "path_to_audio": {
            "description": "Path to audio original location",
            "type": "string"
        },
        "transcription_approach": {
            "description": "Approach for transcription and model size",
            "type": "string"
        },
        "final": {
            "description": "Marker to flag last audio segment in a series",
            "type": "boolean"
        },
        "params": {
            "description": "Audio headers/metadata",
            "type": "string"
        },
        "frames": {
            "description": "Audio content in bytes",
            "type": "string"
        },
        "timestamp": {
            "description": "Time of reading in ms since epoch",
            "type": "number"
        }
    }
}"""


transcription_str = """{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "audio_object",
    "description": "Audio segments",
    "type": "object",
    "properties": {
        "path_to_transcription": {
            "description": "Path to location of transcription",
            "type": "string"
        },
        "transcription_approach": {
            "description": "Approach for transcription and model size",
            "type": "string"
        },
        "content": {
            "description": "Contents of transcription",
            "type": "string"
        },
        "timestamp": {
            "description": "Time of reading in ms since epoch",
            "type": "number"
        }
    }
}"""