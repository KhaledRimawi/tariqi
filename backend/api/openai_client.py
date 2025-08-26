import os
import sys

# resolve path to ../common relative to *this file*
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "common")))

from dotenv import load_dotenv

load_dotenv()
from keyvault_client import get_secret
from openai import AzureOpenAI

# Get values from .env
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
subscription_key = get_secret(os.getenv("OPEN_AI_SECRET_KEY"))

deployment = "gpt-35-turbo"
api_version = "2024-12-01-preview"

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)


def get_gpt_response(user_prompt: str) -> str:
    """
    Takes the user prompt as input and returns GPT's response.
    """
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=4096,
        temperature=1.0,
        top_p=1.0,
        model=deployment,
    )

    return response.choices[0].message.content


# ---- Example ----
if __name__ == "__main__":
    question = input("Write your question: ")
    answer = get_gpt_response(question)
    print("\nAssistant:", answer)
