from openai import OpenAI
import json

# Initialize OpenAI client
client = OpenAI(
    api_key=""  # Add your API key here
)

# System Prompt: Tell the model what you want it to do
system_prompt = """
   YOUR PROMPT HERE
"""

# Read the article content from the file
with open('./section-2/article.txt', 'r', encoding='utf-8') as file:
    article_content = file.read()

# Create a chat completion request to analyze the article
completion = client.chat.completions.create(
    model="gpt-4o",
     messages=[
         #might need to add something here?
        {"role": "user", "content": "Provide a JSON representation of this article:\n" + article_content}
    ],
    #or sometihng here? does this change with what model you use?
)

# Parse the response and print the JSON object
response_content = completion.choices[0].message.content

try:
    analysis_result = json.loads(response_content)  # Convert response to JSON
    print(json.dumps(analysis_result, indent=4))  # Pretty-print the JSON
except json.JSONDecodeError:
    print("Failed to decode the response as JSON. Here is the raw response:")
    print(response_content)

