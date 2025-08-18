import base64
import logging
from azure.identity import DefaultAzureCredential 
from azure.keyvault.secrets import SecretClient


KEY_VAULT_URL = "https://roads-condition-kv.vault.azure.net/"
# logging.basicConfig(level=logging.DEBUG)

credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

SECRET_NAMES = [
    "telegramSessionPart1",
    "telegramSessionPart2",
    "telegramSessionPart3"
]

def get_secret(secret_name: str) :
    """Fetch secret from Azure Key Vault"""
    try:
        secret = secret_client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        raise RuntimeError(f"Unable to fetch secret '{secret_name}': {e}")

def get_session_file(secret_names: list, session_path: str = "telegram_session.session"):
    full_bytes = b""

    for name in secret_names:
        part = get_secret(name)
        full_bytes += base64.b64decode(part)
        print(f"Retrieved secret: {name}")

    with open(session_path, "wb") as f:
        f.write(full_bytes)

    print(f"✅ Session file reconstructed at: {session_path}")
    return session_path  # return the file path


SESSION_FILE_PATH = get_session_file(SECRET_NAMES)

APP_HASH = secret_client.get_secret("appHash").value
MONGO_CONNECTION_STRING = secret_client.get_secret("mongodbConnectionString").value
PHONE_NUMBER = secret_client.get_secret("PhoneNumber").value

print("✅ Secrets fetched: APP_HASH, PHONE_NUMBER, MONGO_CONNECTION_STRING")

