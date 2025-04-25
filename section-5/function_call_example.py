from openai import OpenAI
import pandas as pd
import json

# Initialize OpenAI client
client = OpenAI(
    api_key=""  # Add your API key here
)

# Define the function schema for structured output
tools = [
    {
        "type": "function",
        "function": {
            "name": "summarize_article",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "stance": {"type": "string"},
                    "urgency": {"type": "integer"}
                },
                "required": ["topic", "stance"]
            }
        }
    }
]

tool_choice = {"type": "function", "function": {"name": "summarize_article"}}

# Prompt to guide extraction
system_prompt = """
You are a political analyst. For each article, extract the main topic, the political stance (e.g., liberal, conservative, centrist, neutral), and assign an urgency score from 1 to 5 based on how immediately the topic demands public attention.
"""

# Load articles from CSV
csv_path = "../section-4/articles.csv"
df = pd.read_csv(csv_path).head(5)

article_column = "article_text"

results = []

for i, row in df.iterrows():
    content = row[article_column]

    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ],
       tools=tools,
       tool_choice=tool_choice
    )

    output = completion.choices[0].message.tool_calls[0].function.arguments
    parsed_output = json.loads(output)
    results.append({"id": i, **parsed_output})

# Save the structured results to a new CSV
output_df = pd.DataFrame(results)
output_df.to_csv("/Users/cai529/Github/dpi-681/section-5/structured_articles.csv", index=False)
print("Saved structured results to structured_articles.csv")
