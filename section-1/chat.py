#!/usr/bin/env python3
"""
Generative AI Query CLI using OpenAI API with Error Handling
--------------------------------------------------------------

This script provides a command-line interface to interact with OpenAI's chat models.
Customize the following variables as needed:

  - SYSTEM_PROMPT: Sets the context for the AI assistant.
  - MODEL: Specifies which OpenAI model to use (e.g., "gpt-3.5-turbo").
  - STREAM_CHAIN_OF_THOUGHT: Boolean flag to control streaming output.

Important! Make sure you have your OpenAI API key set in your environment as OPENAI_API_KEY.
"""

import os
import openai
import time
from openai.error import RateLimitError, APIError, APIConnectionError, InvalidRequestError

# -------------------------------
# Configuration Variables
# -------------------------------

# Change the system prompt as you would like
SYSTEM_PROMPT = "You are a helpful assistant specialized in generative AI and public policy."

# The model to be used (e.g., "gpt-3.5-turbo" or "gpt-4").
MODEL = "gpt-3.5-turbo"

# Boolean flag: set to True to stream the chain-of-thought response.
STREAM_CHAIN_OF_THOUGHT = True

# Set your OpenAI API key from the environment variable.
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Missing API key: Please set your OpenAI API key in the OPENAI_API_KEY environment variable.")

# -------------------------------
# Functions
# -------------------------------

def make_query(user_input, system_prompt=SYSTEM_PROMPT, model=MODEL, stream=STREAM_CHAIN_OF_THOUGHT):
    """
    Sends a query to the OpenAI chat model and returns the response.

    Parameters:
        user_input (str): The user's input query.
        system_prompt (str): The system prompt to establish context.
        model (str): The OpenAI model to use.
        stream (bool): If True, stream the chain-of-thought response.

    Returns:
        str: The full response from the AI.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            stream=stream
        )
    except RateLimitError:
        print("Error: Rate limit exceeded. Please wait and try again later.")
        return ""
    except (APIError, APIConnectionError) as e:
        print(f"Error: API error encountered - {e}")
        return ""
    except InvalidRequestError as e:
        print(f"Error: Invalid request - {e}")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""

    full_response = ""
    if stream:
        print("\n[Streaming Response]: ", end="", flush=True)
        try:
            # Iterate over the streamed chunks and print tokens as they arrive.
            for chunk in response:
                if 'choices' in chunk:
                    delta = chunk['choices'][0]['delta']
                    if 'content' in delta:
                        content = delta['content']
                        print(content, end="", flush=True)
                        full_response += content
            print()  # New line after streaming.
        except Exception as e:
            print(f"\nError during streaming response: {e}")
    else:
        try:
            full_response = response.choices[0].message['content']
            print("\n[Response]:", full_response)
        except Exception as e:
            print(f"Error processing response: {e}")

    return full_response

def main():
    """
    Main function to run the command-line interface.
    """
    print("Welcome to the Generative AI Query CLI!")
    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        user_input = input("Enter your query: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Process the query and get the AI's response
        make_query(user_input)

if __name__ == "__main__":
    main()
