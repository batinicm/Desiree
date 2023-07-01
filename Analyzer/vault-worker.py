# Retrieves and manages secrets stored in Azure Key Vault

import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

key_vault_name = os.environ["KEY_VAULT_NAME"]
kv_uri = f"https://{key_vault_name}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=kv_uri, credential=credential)


def get_vault_secret(secret_name):
    print(f"Retrieving your secret from {key_vault_name}.")
    secret = client.get_secret(secret_name)

    return secret
