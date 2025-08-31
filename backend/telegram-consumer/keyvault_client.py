import os
from functools import lru_cache

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient


@lru_cache(maxsize=1)
def _secret_client() -> SecretClient:
    vault_url = os.getenv("KEY_VAULT_URL")
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("AppSecret")
    if not all([vault_url, tenant_id, client_id, client_secret]):
        raise RuntimeError("Missing Key Vault/AAD env vars.")
    cred = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    return SecretClient(vault_url=vault_url, credential=cred)


def get_secret(name: str) -> str:
    try:
        return _secret_client().get_secret(name).value
    except Exception as e:
        raise RuntimeError(f"Unable to fetch secret '{name}': {e}")
