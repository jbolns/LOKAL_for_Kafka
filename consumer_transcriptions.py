# ..................
# SECTION: TOP-LEVEL IMPORTS
# ..................
# Python
import os
from dotenv import load_dotenv

# Kafka core
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.avro import AvroDeserializer

# Kafka helpers and utils
from schemas import avro_schemas
from config import config, sr_config
from utils.conversions import dict_to_txt


# ..................
# SECTION: KAFKA CONSUMER
# Called by watchdog when a new audio hits the source folder or is modified
# Produces message based on location of new audio
# ..................
# Consumer configs
def set_consumer_configs():
    ''' Sets configs specific to consumer
    '''
    config['group.id'] = 'transcriptions_group'
    config['auto.offset.reset'] = 'earliest'


# Main consumer function
def consume(topic):
    ''' Consumes messages and processes them as follows:
        1. Deserialises message
        2. Writes content of transcription to file.
    '''
    
    # Function specific imports
    import os
    from dotenv import load_dotenv
    load_dotenv()

    # Set destination folder
    path_to_destination_folder = os.getenv('LOCAL_NODE_OUTPUT_FOLDER')
    
    # Set consumer configs
    set_consumer_configs()

    # Set schema
    schema_str = avro_schemas.transcription_str
    schema_registry_client = SchemaRegistryClient(sr_config)
    
    # Set deserialiser
    avro_deserializer = AvroDeserializer(schema_registry_client, schema_str, from_dict=dict_to_txt)
    
    # Consume like a degenerate
    consumer = Consumer(config)
    consumer.subscribe([topic])

    print('\nTranscriptions consumer is running.')

    while True:
        
        try:
            event = consumer.poll(1.0)
            
            if event is None:
                continue

            transcription_in = avro_deserializer(event.value(), SerializationContext(topic, MessageField.VALUE))
            
            if transcription_in is not None:
                
                # Announce new message
                print(f'\n------\nNew message available.\
                      \nOriginal audio location: {transcription_in.path_to_transcription}. Transcription approach: {transcription_in.transcription_approach}.')

                # Write to file
                try:
                    filename = transcription_in.path_to_transcription.split('\\')[-1]
                    with open(f'{path_to_destination_folder}\\{filename}', 'w') as f:
                        f.write(transcription_in.content)
                        f.close
                except Exception as e:
                    print(f'Failed to consumer transcription.\nError: {e}')

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
        topic = 'transcriptions_avro'
    elif schema_type == 'json':
        topic = 'transcriptions_json'
    
    # Run consumer
    consume(topic)