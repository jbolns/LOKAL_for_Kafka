'''
LOKAL for Kafka (LfK), v1. May 2024.
@author: Dr J.

To be fair, this file is barely my code. The file is based on this approach:
https://developer.confluent.io/courses/kafka-python/adminclient-class-hands-on/

with minor mods to create Avro or JSON topics as determined by .env.

'''

# ..................
# SECTION: TOP-LEVEL IMPORTS
# ..................
import os
import time
from dotenv import load_dotenv
from confluent_kafka.admin import (AdminClient, NewTopic, ConfigResource)
from config import config

# ..................
# SECTION: Topic creation
# Called to check if a topic exist and create if not
# ..................
def topic_exists(admin, topic):
    ''' Checks if topic exists
        Returns true if so.
    '''

    metadata = admin.list_topics()

    for t in iter(metadata.topics.values()):
        if t.topic == topic:
            return True
    return False


def create_topic(admin, topic):
    ''' Create new topic
        Return results dictionary
    '''
    
    new_topic = NewTopic(topic, num_partitions=6, replication_factor=3) 
    result_dict = admin.create_topics([new_topic])
    
    for topic, future in result_dict.items():
    
        try:
            future.result()  # The result itself is None
            print("Topic {} created".format(topic))
    
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))


# ..................
# SECTION: Message size
# Called to check and reset a topic's max message size
# ..................
def get_max_size(admin, topic):
    ''' Get max.message.bytes property
    '''
    
    resource = ConfigResource('topic', topic)
    result_dict = admin.describe_configs([resource])
    config_entries = result_dict[resource].result()
    max_size = config_entries['max.message.bytes']
    
    return max_size.value


def set_max_size(admin, topic, max_k):
    ''' Set Max.message.bytes for topic
    '''
    config_dict = {'max.message.bytes': str(max_k)}
    resource = ConfigResource('topic', topic, config_dict)
    result_dict = admin.alter_configs([resource])
    result_dict[resource].result()


# ..................
# SECTION: KAFKA ADMIN
# Called to check and create a list of desired topics
# ..................
def check_create_topic(topic_name):
    ''' Handles flow of actions needed to:
        (1) Check if a topic exists
        (2) Create topic if it does not exist
        (3) Check if max message size equals desired max (set in .env)
        (4) Reset max message size if needed
    '''

    # Create Admin client
    admin = AdminClient(config)
    
    # Create topic if it doesn't exist
    if not topic_exists(admin, topic_name):
        create_topic(admin, topic_name)
    
    # Chill a bit to ensure changes are applied
    time.sleep(3)

    # Check max.message.bytes config
    current_max = get_max_size(admin, topic_name)
    print(f'Topic, {topic_name} max.message.bytes is {current_max}, roughly {int(int(current_max)/(1024*1024))} MB.')

    # Chill a bit
    time.sleep(3)
    
    # Optional. Change max size
    new_max = int(os.getenv('MAX_MESSAGE_SIZE'))  # Enter max in bytes
    if current_max != str(new_max):
        print(f'Topic, {topic_name} max.message.bytes is {current_max}.')
        set_max_size(admin, topic_name, new_max)

        # Chill a bit
        time.sleep(3)

        # Verify change
        new_current_max = get_max_size(admin, topic_name)
        print(f'Now max.message.bytes for topic {topic_name} is {new_current_max}, roughly {int(int(new_current_max)/(1024*1024))} MB')


# ..................
# SECTION: NAME-MAIN
# Triggers watch-produce sequence
# ..................
if __name__ == '__main__':
    
    # Load environment
    load_dotenv()

    # Give the names of all topics wanted
    if os.getenv('SCHEMA_TYPE').lower() == 'json':
        list_of_topics = ['audio_json', 'transcriptions_json'] 
    else:
        list_of_topics = ['audio_avro', 'transcriptions_avro'] 

    for topic in list_of_topics:
        check_create_topic(topic)