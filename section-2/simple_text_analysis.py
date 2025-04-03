from openai import OpenAI
import json

# Initialize OpenAI client
client = OpenAI(
    api_key=""  # Add your API key here
)

# System Prompt: Tell the model what you want it to do
system_prompt = """
    You are an expert textual analyst.
    Your task is to analyze the content of news articles and provide the following in JSON format:
    - A short summary
    - Key points
    - Social Issues Raised 
    - Political Slant
    - Sentiment 
    You provide your response in JSON format.

    The JSON response should look like:
    {{
        "summary": "short summary of the article",
        "key_points": ["point 1", "point 2", ...],
        "social_issues": ["issue 1", "issue 2", ...],
        "political_slant": right/left/neutral,
        "sentiment": positive/negative/neutral
    }}

    For key_points, social_issues, and political_slant, provide a list of items.
    For sentiment, provide a string indicating the sentiment (e.g., "positive", "negative", "neutral").
    Respond only with the JSON object, without any additional text or explanation.
"""

# Read the article content from the file
with open('./section-2/article.txt', 'r', encoding='utf-8') as file:
    article_content = file.read()

# Create a chat completion request to analyze the article
completion = client.chat.completions.create(
    model="o3-mini",
     messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Provide a JSON representation of this article:\n" + article_content}
    ],
)

# Parse the response and print the JSON object
response_content = completion.choices[0].message.content

try:
    analysis_result = json.loads(response_content)  # Convert response to JSON
    print(json.dumps(analysis_result, indent=4))  # Pretty-print the JSON
except json.JSONDecodeError:
    print("Failed to decode the response as JSON. Here is the raw response:")
    print(response_content)

