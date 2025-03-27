import os
from openai import OpenAI
import openai
import time

# -------------------------------
# API Key and System Prompt Settings
# -------------------------------

# Explicitly set your OpenAI API key here:
OPENAI_API_KEY = ""  # Replace with your actual API key

# Set the system prompt (context for the AI assistant) here:
SYSTEM_PROMPT = "You are a helpful assistant specialized in generative AI and public policy."

# Set your OpenAI API key from the variable or fallback to environment variable.
openai.api_key = OPENAI_API_KEY if OPENAI_API_KEY else os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Missing API key: Please set your OpenAI API key in the code or as an environment variable.")

# -------------------------------
# Configuration Variables
# -------------------------------

# The model to be used (set to the newest client model, e.g., "gpt-4")
MODEL = "gpt-4"

# Boolean flag: set to True to stream the chain-of-thought response.
STREAM_CHAIN_OF_THOUGHT = True

# Instantiate the client
client = OpenAI(api_key=OPENAI_API_KEY)

# Global conversation history: stores a list of messages (each a dict with 'role' and 'content')
conversation_history = []

# -------------------------------
# Functions
# -------------------------------

def make_query(user_input, system_prompt=SYSTEM_PROMPT, model=MODEL, stream=STREAM_CHAIN_OF_THOUGHT):
    """
    Sends a query to the OpenAI chat model with the previous context and returns the response.

    Parameters:
        user_input (str): The user's input query.
        system_prompt (str): The system prompt to establish context.
        model (str): The OpenAI model to use.
        stream (bool): If True, stream the chain-of-thought response.

    Returns:
        str: The full response from the AI.
    """
    global conversation_history

    # Build the messages list: include the system message and last 10 conversation messages.
    # Note: conversation_history already contains both user and assistant messages.
    context = conversation_history[-10:]
    messages = [{"role": "system", "content": system_prompt}] + context

    # If the latest user query isn't in the conversation history yet, add it.
    if not context or context[-1].get("role") != "user" or context[-1].get("content") != user_input:
        messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream
        )
    except openai.RateLimitError:
        print("Error: Rate limit exceeded. Please wait and try again later.")
        return ""
    except (openai.APIError, openai.APIConnectionError) as e:
        print(f"Error: API error encountered - {e}")
        return ""
    except openai.BadRequestError as e:
        print(f"Error: Invalid request - {e}")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""

    full_response = ""
    
    if stream:
        print("\nOpenAI API: ", end="", flush=True)
        try:
            # Iterate over the streamed chunks and print tokens as they arrive.
            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    # Check if delta.content exists before printing
                    if delta.content:
                        content = delta.content
                        print(content, end="", flush=True)
                        full_response += content
            print()  # New line after streaming.
        except Exception as e:
            print(f"\nError during streaming response: {e}")
    else:
        try:
            full_response = response.choices[0].message.content
            print("\nOpen API:", full_response)
        except Exception as e:
            print(f"Error processing response: {e}")

    return full_response

def main():
    """
    Main function to run the command-line interface.
    """
    global conversation_history
    print("Welcome to the ChatGPT-CLI!")
    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        user_input = input("Enter your query: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Append the user's message to the conversation history.
        conversation_history.append({"role": "user", "content": user_input})

        # Process the query and get the AI's response.
        assistant_response = make_query(user_input)

        # Append the assistant's response to the conversation history.
        if assistant_response:
            conversation_history.append({"role": "assistant", "content": assistant_response})

if __name__ == "__main__":
    main()
