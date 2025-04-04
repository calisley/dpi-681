import pandas as pd
from openai import OpenAI
from tqdm import tqdm

# Load articles from CSV (expected to have "id" and "article_text" columns)
df = pd.read_csv("./articles.csv")

# Initialize OpenAI client
client = OpenAI(
    api_key=""  # Add your API key here
)

# System prompt defining the analysis requirements
system_prompt = """
"""

# List to store analysis results for each article
results = []

# Iterate over DataFrame rows with a progress bar
for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Analyzing Articles"):
    article_text = row["truncated_article"]  # Use the truncated article text
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Analyze the following news article as instructed" + article_text}
        ],
    )
    response_content = completion.choices[0].message.content
    results.append(response_content)

# Convert the list of analysis dictionaries into a DataFrame
df["analysis_result"] = results

# Save the updated DataFrame to a new CSV file
df.to_csv("./articles_with_analysis_columns.csv", index=False)

print("Article analysis complete. Results saved to articles_with_analysis_columns.csv")
