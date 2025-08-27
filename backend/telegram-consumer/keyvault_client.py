import os

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient


def get_secret(secret_name: str):
    """Fetch secret from Azure Key Vault"""
    secret_client = SecretClient(vault_url=os.getenv("KEY_VAULT_URL"), credential=ClientSecretCredential(
        tenant_id=os.getenv("TENANT_ID"),
        client_id=os.getenv("CLIENT_ID"),
        client_secret=(os.getenv("AppSecret"))))
    try:
        secret = secret_client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        raise RuntimeError(f"Unable to fetch secret '{secret_name}': {e}")
