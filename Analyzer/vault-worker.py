# Retrieves and manages secrets stored in Azure Key Vault

import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

key_vault_name = "desiree-vault"
kv_uri = f"https://{key_vault_name}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=kv_uri, credential=credential)


if __name__ == '__main__':
    print(f"Retrieving your secret from {key_vault_name}.")
    secret = client.get_secret("LanguageAnalyzerEndpoint")

    print(secret)
