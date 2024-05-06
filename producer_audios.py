# ..................
# SECTION: TOP-LEVEL IMPORTS
# ..................
# Python
import os
import time
import json
import mimetypes
from dotenv import load_dotenv

# Watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Kafka core
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.schema_registry.json_schema import JSONSerializer

# Kafka helpers and utils
from config import config, sr_config
from schemas import avro_schemas, json_schemas
from utils.classes import KafkaAudio
from utils.conversions import audio_to_chunks, audio_to_data, audio_to_dict

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
                
                print(f'\nFile {event.event_type}. Location: {event.src_path}. Timestamp: {timestamp}.')
                
                # Produce only if file is audio
                file_type = mimetypes.guess_type(event.src_path)[0].split('/')[0]        
                if file_type == 'audio':
                    produce(event.src_path)
                else:
                    print('No Kafka actions where taken because file is not in .wav format')

        except Exception as e:
            print('Oooops, something went wrong while producing this message.\
                  \nProducer will trying to recover and continue with next message.')


# ..................
# SECTION: KAFKA PRODUCER
# Called by watchdog when a new audio hits the source folder or is modified
# Produces message based on location of new audio
# ..................
def delivery_report(err, event):
    ''' Callback function to communicate success or failure
    '''
    if err is not None:
        print(f'Delivery failed on reading for {event.key()}: {err}')
    else:
        print(f'Message produced to {event.topic()}')


def produce(path_to_audio):
    ''' Main producer
    '''

    from base64 import b64encode
    from utils.utils import recommended_chunk_size

    # Extract message metadata from path into variables
    try:
        
        # Define topic
        schema_type = os.getenv('SCHEMA_TYPE').lower()
        if schema_type == 'avro':
            topic = 'audio_avro'
        elif schema_type == 'json':
            topic = 'audio_json'

        # Get transcription approach model size from path
        # Solution here longer than path splitting, but more flexible
        
        if path_to_audio.find('\\segmentation\\') > 0:
            transcription_approach = 'segmentation'
        elif path_to_audio.find('\\diarisation\\') > 0:
            transcription_approach = 'diarisation'
        else:
            transcription_approach = 'simple'

        if path_to_audio.find('\\base\\') > 0:
            transcription_approach = transcription_approach + '.base'
        elif path_to_audio.find('\\small\\') > 0:
            transcription_approach = transcription_approach + '.small'
        elif path_to_audio.find('\\medium\\') > 0:
            transcription_approach = transcription_approach + '.medium'
        elif path_to_audio.find('\\large\\') > 0:
            transcription_approach = transcription_approach + '.large'
        else:
            transcription_approach = transcription_approach + '.tiny'
    
    except Exception as e:
        print(f'Producer unable to determine transcription approach or model size from filepath: {e}')

    # Connect to schema registry
    # (Set schema to Avro or JSON using SCHEMA_TYPE in .env)
    try:
        schema_registry_client = SchemaRegistryClient(sr_config)
        if schema_type == 'avro':
            schema_str = avro_schemas.audio_str
            serializer = AvroSerializer(schema_registry_client, schema_str, to_dict=audio_to_dict)
        elif schema_type == 'json':
            schema_str = json_schemas.audio_str
            serializer = JSONSerializer(schema_str, schema_registry_client, to_dict=audio_to_dict)
    except Exception as e:
        print(f'Producer was unable to connect to schema registry: {e}')

    # Break audio into chunks to ensure message is under Kafka size limits
    try:
        max_duration = recommended_chunk_size(path_to_audio, schema_type)
        #max_duration = 4 * 1000
        print(f'Audio will be chunked into {int(max_duration / 1000)}s long segments')
        chunks = audio_to_chunks(path_to_audio, max_duration)
    except Exception as e:
        print(f'Producer was unable to break audio into small message chunks: {e}')

    # Messaging loop (send a message per chunk)
    # Fault-tolerance appraoch: 
    # 1. continue to next if message unsuccesful
    # 2. let producer die if loop itself errors out
    try:
        for i, chunk in enumerate(chunks):
            try:
                # Announce message
                print(f'Sending audio chunk {i+1} of {len(chunks)}')
                
                # Convert audio into data that can travel easily
                params, frames = audio_to_data(chunk)

                # Flag final chunk in series of audios
                # (needed to trigger audio rebuild)
                final = 1 if i + 1 == len(chunks) else 0

                # Create message
                audio_out = KafkaAudio(path_to_audio, transcription_approach, final, params, frames, round(time.time()*1000))
                
                # If using JSON schema, adjust message fields for compatibility
                if schema_type == 'json':
                    # Number booleans into True/False
                    audio_out.final = True if audio_out.final == 1 else False
                    
                    # Bytes to string
                    encoding = json.detect_encoding(audio_out.frames)
                    try:
                        base64_bytes = b64encode(audio_out.frames)
                        base64_string = base64_bytes.decode(encoding)
                        audio_out.frames = base64_string
                    except:
                        if 'utf-' in encoding:
                            encoding = 'utf-8'
                            base64_bytes = b64encode(audio_out.frames)
                            base64_string = base64_bytes.decode(encoding)
                            audio_out.frames = base64_string
                        else:
                            pass

                    # Append string to something that's travelling anyway
                    audio_out.params = audio_out.params + ',' + encoding

                # Construct the value of message
                message = serializer(audio_out, SerializationContext(topic, MessageField.VALUE))

                # Produce the message
                producer = Producer(config)
                producer.produce(topic=topic, key=str(audio_out.transcription_approach), value=message, on_delivery=delivery_report)

                # Flush the producer
                producer.flush()

            except Exception as e:
                print(f'Producer was unable to send message chunk #{i+1} of {len(chunks)}: {e}')
                continue

    except Exception as e:
        print(f'Producer main loop failed unexpectedly: {e}')





# ..................
# SECTION: NAME-MAIN
# Triggers watch-produce sequence
# ..................
if __name__ == '__main__':
    
    # Load environment
    load_dotenv()

    # Run producer
    Watch(os.getenv('SOURCE_FOLDER')).run()