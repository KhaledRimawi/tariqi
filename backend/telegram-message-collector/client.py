import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from appsecrets import OPEN_AI_CLIENT

# Load .env variables
load_dotenv()

# Get values from .env
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
subscription_key = OPEN_AI_CLIENT

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
