
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
# File contains key Kafka configurations

# ..................
# TOP-LEVEL IMPORTS
# ...
import os
from dotenv import load_dotenv

# ..................
# ENVIRONMENT
# ...
load_dotenv()

# ..................
# CONFIGS
# ...

# Main configs
config = {
    'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv('API_KEY'),
    'sasl.password': os.getenv('API_SECRET')
    } if os.getenv('KAFKA_PLATFORM').lower() == 'confluent' else {
        'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS')
        } if os.getenv('KAFKA_PLATFORM').lower() == 'other' else {
            ''
            }

# Schema registry
sr_config = {
    'url': os.getenv('SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f'{os.getenv("SCHEMA_REGISTRY_KEY")}:{os.getenv("SCHEMA_REGISTRY_SECRET")}'
    } if os.getenv('KAFKA_PLATFORM').lower() == 'confluent' else {
        'url': os.getenv('SCHEMA_REGISTRY_URL')
        } if os.getenv('KAFKA_PLATFORM').lower() == 'other' else {
            ''
        }
