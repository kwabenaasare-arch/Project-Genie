# ai_helper.py
# A single function that sends a prompt to Claude and returns the response
# Test this file independently before connecting it to Slack

import anthropic
import os
from dotenv import load_dotenv

load_dotenv()  # Reads your .env file so the API key is available

def get_ai_response(prompt: str) -> str:
    """
    Takes a prompt string.
    Sends it to Claude.
    Returns the reply as a plain string.
    """

    # Create a connection to the Anthropic API
    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"]
    )

    # Send the prompt and get a response
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Pull the text out of the response and return it
    return message.content[0].text


# -----------------------------------------------
# TEST BLOCK — only runs when you run this file directly
# Won't run when imported by main.py or other files
# -----------------------------------------------
if __name__ == "__main__":
    test_prompt = "Summarise what a personal assistant bot does in 2 sentences."

    print("Sending prompt to Claude...")
    print(f"Prompt: {test_prompt}")
    print("-" * 40)

    response = get_ai_response(test_prompt)

    print("Response:")
    print(response)
