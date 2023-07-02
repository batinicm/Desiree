# Retrieves and manages secrets stored in Azure Key Vault
# IMPORTANT: in order for this to work, environment variables for service principal need to be set up
#   Reference: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TROUBLESHOOTING.md#troubleshoot-environmentcredential-authentication-issues
#   Service principal secrets stored in desiree-vault

import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

key_vault_name = "desiree-vault"
kv_uri = f"https://{key_vault_name}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=kv_uri, credential=credential)


def get_secret(secret_name):
    print(f"Retrieving your secret from {key_vault_name}.")
    secret = client.get_secret(secret_name)

    return secret.value
