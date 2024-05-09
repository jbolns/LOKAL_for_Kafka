
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
import os
from dotenv import load_dotenv

# ..................
# SECTION: ENVIRONMENT
# ..................
load_dotenv()

# ..................
# SECTION: CONFIGS
# ..................
config = {
    'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS'),     
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv('API_KEY'),
    'sasl.password': os.getenv('API_SECRET')
}

sr_config = {
    'url': os.getenv('SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f'{os.getenv("SCHEMA_REGISTRY_KEY")}:{os.getenv("SCHEMA_REGISTRY_SECRET")}'
}