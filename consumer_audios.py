# ..................
# SECTION: TOP-LEVEL IMPORTS
# ..................
# Python
import os
import threading
from dotenv import load_dotenv

# Kafka core
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.schema_registry.json_schema import JSONDeserializer

# Kafka helpers and utils
from schemas import avro_schemas, json_schemas
from config import config, sr_config
from utils.conversions import dict_to_audio, data_to_audio

# LOKAL transcriptions
from utils.lokal_transcribe import run_transcription

# ..................
# SECTION: KAFKA CONSUMER
# Called by watchdog when a new audio hits the source folder or is modified
# Produces message based on location of new audio
# ..................
# Consumer configs
def set_consumer_configs():
    ''' Sets configs specific to this consumer
    '''

    config['group.id'] = 'audios_group'
    config['auto.offset.reset'] = 'earliest'


# Main consumer function
def consume(topic, schema_type):
    ''' Consumes messages and processes them as follows:
        1. Deserialises message
        2. If message is NOT the last in a series of audio chunks:
            accumulates message
        3. If message is the last in a series of audio chunks:
            reconstructs audio using messages acccumulated thus far
        4. If audio reconstruction is triggered:
            transcribes reconstructed audio.
    '''
    
    # Initialise array to join frames of any audio chunks
    JOINT_FRAMES = []

    # Set consumer configs
    set_consumer_configs()

    # Set schema
    # Connect to schema registry
    # (Set schema to Avro or JSON using SCHEMA_TYPE in .env)
    try:
        schema_registry_client = SchemaRegistryClient(sr_config)
        if schema_type == 'avro':
            schema_str = avro_schemas.audio_str
            deserializer = AvroDeserializer(schema_registry_client, schema_str, from_dict=dict_to_audio)
        elif schema_type == 'json':
            schema_str = json_schemas.audio_str
            deserializer = JSONDeserializer(schema_str, from_dict=dict_to_audio)
    except Exception as e:
        print(f'Producer was unable to connect to schema registry: {e}')
    
    # Consume like a degenerate
    consumer = Consumer(config)
    consumer.subscribe([topic])

    print('\nAudio consumer is running.')

    while True:
        
        try:
            event = consumer.poll(1.0)
            
            if event is None:
                continue

            audio_in = deserializer(event.value(), SerializationContext(topic, MessageField.VALUE))
            
            
            if audio_in is not None:

                # Announce new message
                print(f'\n------\nNew message available.\
                      \nType: {audio_in.transcription_approach}. Original location: {audio_in.path_to_audio}. Last chunk: {audio_in.final}')

                # If using JSON schema, adjust frame field for compatibility
                if schema_type == 'json':

                    # Get encoding from params and restore params to original format
                    all_params = audio_in.params.split(',')
                    audio_in.params = ','.join(all_params[:-1])
                    encoding = all_params[-1]

                    from base64 import b64decode
                    base64_bytes = audio_in.frames.encode(encoding)
                    pure_bytes = b64decode(base64_bytes)
                    audio_in.frames = pure_bytes
                    

                # Accumulate frames with any pre-existing frames in same series
                JOINT_FRAMES.append(audio_in.frames)
                
                # If message is the last chunk, reconstruct and transcribe
                if audio_in.final == 1 or audio_in.final is True:
                    print('final audio has arrived')
                    
                    # Join frames of all chunks
                    try:
                        frames = b''.join(JOINT_FRAMES)
                    except Exception as e:
                        print(f'Failed to join frames.\nError: {e}')

                    # Reset array for framesJoin frames of all chunks
                    try:
                        JOINT_FRAMES = []
                    except Exception as e:
                        print(f'Failed to reset array used to accumulate frames. Expect errors in next audio.\nError: {e}')
                    
                    # Reconstruct audio
                    try:
                        filename = audio_in.path_to_audio.rsplit('\\')[-1].rsplit('.')[0]
                        path_to_temp_audio = data_to_audio(audio_in.params, frames, filename)
                    except Exception as e:
                        print(f'Failed to reconstruct audio.\nError: {e}')

                    # Transcribe audio
                    try:
                        transcription_thread = threading.Thread(target=run_transcription(path_to_temp_audio, audio_in.transcription_approach, filename), daemon=True)
                        transcription_thread.start()
                    except Exception as e:
                        print(f'Failed to transcribed reconstructed audio.\nError: {e}')

        except KeyboardInterrupt:
            break

        except Exception as e:
            print(f'There was an error with this message: {e}.\nConsumer will continue to next message.')

    consumer.close()


# ..................
# SECTION: NAME-MAIN
# Triggers watch-produce sequence
# ..................
if __name__ == '__main__':
    
    # Load environment variables
    load_dotenv()

    # Define topic
    schema_type = os.getenv('SCHEMA_TYPE').lower()
    if schema_type == 'avro':
        topic = 'audio_avro'
    elif schema_type == 'json':
        topic = 'audio_json'
    
    # Start the consumer
    consume(topic, schema_type)