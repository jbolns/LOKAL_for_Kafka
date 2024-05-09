'''
LOKAL for Kafka (LfK), v1. May 2024.
@author: Dr J.

Except for absolutely necessary classes, LfK tries to stick to a functional programming paradigm.
Any classes must be justified exceptionally well.

Copyright (c) 2024 Jose A Bolanos / Polyzentrik Tmi.
SPDX-License-Identifier: Apache-2.0.

'''

audio_str = """{
    "type": "record",
    "namespace": "confluent_kafka.schema_registry.avro",
    "name": "audio_object",
    "fields": [
        {"name": "path_to_audio", "type": "string"},
        {"name": "transcription_approach", "type": "string"},
        {"name": "final", "type": "boolean"},
        {"name": "params", "type": "string"},
        {"name": "frames", "type": "bytes"},
        {"name": "timestamp", "type": { "type": "int", "logicalType": "timestamp-millis" }}
    ]
}"""


transcription_str = """{
    "type": "record",
    "namespace": "confluent_kafka.schema_registry.avro",
    "name": "transcription_object",
    "fields": [
        {"name": "path_to_transcription", "type": "string"},
        {"name": "transcription_approach", "type": "string"},
        {"name": "content", "type": "string"},
        {"name": "timestamp", "type": { "type": "int", "logicalType": "timestamp-millis" }}
    ]
}"""