
import anthropic
import os
import time
import random

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

key = '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'

def demo():
    client = anthropic.Anthropic(api_key=key)  # Initialize the Anthropic client with your API key

    # Creating a message
    response = client.beta.messages.create(
        model="claude-2.1",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": "Hello there."},
            {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
            {"role": "user", "content": "Can you explain LLMs in plain English?"},
        ]
    )

    print(response.content[0].text)