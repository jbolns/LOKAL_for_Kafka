'''
LOKAL for Kafka (LfK), v1. May 2024.
@author: Dr J.

Except for absolutely necessary classes, LfK tries to stick to a functional programming paradigm.
Any classes must be justified exceptionally well.

Copyright (c) 2024 Jose A Bolanos / Polyzentrik Tmi.
SPDX-License-Identifier: Apache-2.0.

'''

# ..................
# SECTION: TOP-LEVEL IMPORTS
# ..................
# Python
import os
import time
from dotenv import load_dotenv

# Watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Kafka core
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

# Kafka helpers and utils
from config import config, sr_config
from schemas import avro_schemas
from utils.classes import KafkaTranscription
from utils.conversions import txt_to_dict


# ..................
# SECTION: WATCHDOG
# Keeps an eye on source folder
# Triggers producer when new audios are available
# ..................
class Watch(FileSystemEventHandler):
    ''' Watches for changes in a source folder
    '''
    
    def __init__(self, path):
        self.observer = Observer()
        self.event_handler = ActionHandler()
        self.path = path

    def run(self):

        try:
            print(f'Watching "{self.path}" for file changes...')
            self.observer.schedule(self.event_handler, self.path, recursive=True)
            self.observer.start()

            while True:
                time.sleep(100)  # Thread sleep time
        
        except KeyboardInterrupt:
            self.observer.stop()
        
        self.observer.join()


class ActionHandler(FileSystemEventHandler):
    ''' Triggers producer when called by Watcher
    '''
    
    @staticmethod
    def on_any_event(event):
        ''' F(x) handles file events in folder being watched
        '''

        try:
            # Record timestamp for action
            timestamp = round(time.time()*1000)
            
            # Handle actions
            # Triggers a message only if audio is created or modified
            if event.is_directory:  # No need to track folder actions
                return None
            elif event.event_type == 'deleted':  # No message needed (Message deletion in Kafka is optional, and handled separately)
                return None
            elif event.event_type == 'created':  # No message needed (Watchdog follows creations with a modification alert)
                return None
            else:
                
                # Produce only if file is transcription text file
                if event.src_path.endswith('_lfkcach3.txt'):
                    pass
                elif not event.src_path.endswith('.txt'):
                    pass
                else:
                    print(f'\nFile {event.event_type}: {event.src_path}. Timestamp: {timestamp}.')
                    
                    # There is a need to avoid duplicated Watchdog events generating redundant messages
                    
                    # Get cache with content of last message and compare with new message
                    new_message = open(event.src_path, 'r').read()
                    path_to_message_cache = '\\'.join(event.src_path.split('\\')[:-1]).replace('\\\\', '\\') + '\\_lfkcach3.txt'
                    try:
                        
                        # Produce is new message is different to last message
                        old_message = open(path_to_message_cache, 'r').read()
                        if new_message != old_message:
                            produce(event.src_path)
                        else:
                            print('Duplicate event. Ignoring.')
                    
                    # Exception kicks in if cache not available, e.g., after starting producer
                    except:
                        produce(event.src_path)
                        # Rewrite message cache after producing message
                    
                    # Rewrite message cache after producing message
                    # Handled after try-except blog because, 
                    # If message not produced, new message is old.
                    with open(path_to_message_cache, 'w') as f:
                        f.write(new_message)
                    
                    # Delete transcription from server after it has been produced
                    central_backups = (os.getenv('CENTRAL_BACKUPS', 'False') == 'True')
                    if central_backups == False:
                        os.remove(event.src_path)

        except Exception as e:
            if str(e).find('[Errno 2] No such file or directory') >= 0:
                print('Duplicate event. Ignoring.')
            else: 
                print('Oooops, ' , e)
            #something went wrong with this message. Producer will try to continue with next message.\n


# ..................
# SECTION: KAFKA PRODUCER
# Called by watchdog when a new transcription hits transcription folder
# ..................
def delivery_report(err, event):
    ''' Callback function to communicate success or failure
    '''
    if err is not None:
        print(f'Delivery failed on reading for {event.key()}: {err}')
    else:
        print(f'Message produced to {event.topic()}')


def produce(path_to_transcription):
    ''' Main producer
    '''

    try:
        # Define topic
        schema_type = os.getenv('SCHEMA_TYPE').lower()
        if schema_type == 'avro':
            topic = 'transcriptions_avro'
        elif schema_type == 'json':
            topic = 'transcriptions_json'

        # Get original transcription approach from path
        if path_to_transcription.find('\\segmentation\\') > 0:
            transcription_approach = 'segmentation'
        elif path_to_transcription.find('\\diarisation\\') > 0:
            transcription_approach = 'diarisation'
        else:
            transcription_approach = 'simple'

        if path_to_transcription.find('\\base\\') > 0:
            transcription_approach = transcription_approach + '.base'
        elif path_to_transcription.find('\\small\\') > 0:
            transcription_approach = transcription_approach + '.small'
        elif path_to_transcription.find('\\medium\\') > 0:
            transcription_approach = transcription_approach + '.medium'
        elif path_to_transcription.find('\\large\\') > 0:
            transcription_approach = transcription_approach + '.large'
        else:
            transcription_approach = transcription_approach + '.tiny'

    except Exception as e:
        print(f'Unable to determine original transcription approach from transcription path: {e}')

    # Connect to schema registry
    try:
        schema_str = avro_schemas.transcription_str
        schema_registry_client = SchemaRegistryClient(sr_config)
        avro_serializer = AvroSerializer(schema_registry_client, schema_str, to_dict=txt_to_dict)
    except Exception as e:
        print(f'Producer was unable to connect to schema registry: {e}')

    # Send message
    try:
        print(f'Sending transcription')
        
        # Create message
        with open(path_to_transcription, 'r') as f:
            content = f.read()
            f.close
        
        transcription_out = KafkaTranscription(path_to_transcription, transcription_approach, content, round(time.time()*1000))
        message = avro_serializer(transcription_out, SerializationContext(topic, MessageField.VALUE))

        # Produce message
        producer = Producer(config)
        producer.produce(topic=topic, key=transcription_out.transcription_approach, value=message, on_delivery=delivery_report)

        # Flush producer
        producer.flush()
    except Exception as e:
        print(f'Producer was unable to send {path_to_transcription}: {e}')



# ..................
# SECTION: NAME-MAIN
# Triggers watch-produce sequence
# ..................
if __name__ == '__main__':
    
    # Load environment
    load_dotenv()

    # Run producer
    Watch(os.getenv('MAIN_NODE_TRANSCRIPTIONS_FOLDER')).run()