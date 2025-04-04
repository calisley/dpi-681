from openai import OpenAI
import json

# Initialize OpenAI client
client = OpenAI(
    api_key=""  # Add your API key here
)

# CHALLENGE: Using the prompt engineering tools you learned this week, design a prompt that extracts something you might want to know about the article. 
# This should be something you might want to convert into data to analyse later, like political slant, sentiment, or a rating of the article's quality

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
        {"role": "user", "content": "Analyze this article as instructed:\n" + article_content}
    ],
    #or sometihng here? does this change with what model you use?
)

# Parse the response and print the JSON object
response_content = completion.choices[0].message.content
print("The model returned:" + response_content)

