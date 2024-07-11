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
# File containst JSON schema strings, used by Kafka producers and consumers


# ..................
# SHEMA STRINGS
# ...
# Schema for messaging/broadcasting system events
event_broadcast_str = """{
    "$schema": "https://json-schema.org/draft-07/schema#",
    "$id": "memory-change-response.json",
    "title": "Storage Change Response",
    "description": "A schema to update the network on filesystem operations",
    "type": "object",
    "properties": {
        "event_type": {
            "description": "The type of event",
            "type": "string"
        },
        "path": {
            "description": "The path of the memory item",
            "type": "string"
        },
        "operation_metadata": {
            "description": "Metadata about operation or for future operations",
            "type": "object",
            "additionalProperties": true
        }
    }
}"""

# Schema for messaging transcription outputs
transcription_str = """{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "final_transcriptions",
    "description": "A schema to use when messaging finalised transcriptions",
    "type": "object",
    "properties": {
        "path_to_transcription": {
            "description": "Path to location of transcription",
            "type": "string"
        },
        "metadata": {
            "description": "Settings used during transcription",
            "type": "string"
        },
        "content": {
            "description": "Transcribed contents of audio",
            "type": "string"
        },
        "timestamp": {
            "description": "Time of reading in ms since epoch",
            "type": "number"
        }
    }
}"""
