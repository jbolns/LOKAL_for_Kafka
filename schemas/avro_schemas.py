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