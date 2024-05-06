import os
from dotenv import load_dotenv

load_dotenv()

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