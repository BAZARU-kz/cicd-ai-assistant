import os
import hvac
from dotenv import dotenv_values, set_key

# Load existing .env file
env_vars = dotenv_values('.env')

# Initialize Vault client
VAULT_ADDR = os.environ["VAULT_ADDR"]
VAULT_TOKEN = os.environ["VAULT_TOKEN"]
VAULT_NAMESPACE = os.environ["VAULT_NAMESPACE"]
APPLICATION = os.environ["APPLICATION"]
ENVIRONMENT = os.environ["ENVIRONMENT"]
PROJECT_NAME = "ai-assistant"

client = hvac.Client(
    url=VAULT_ADDR,
    token=VAULT_TOKEN,
    namespace=VAULT_NAMESPACE
)

def read_secret():
    print(f'VAULT Is authenticated: {client.is_authenticated()}')
    read_response = client.secrets.kv.v2.read_secret_version(
        path=f'data/{PROJECT_NAME}/{ENVIRONMENT}/{APPLICATION}/',
        mount_point='secret'
    )
    pass_list = read_response['data']['data']
    
    with open('.env', 'w') as f:
        for key, value in pass_list.items():
            set_key('.env', key, value)
            env_vars[key] = value
        
        for key, value in env_vars.items():
            f.write(f'{key}={value}\n')

read_secret()