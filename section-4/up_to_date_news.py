import requests
import pandas as pd
from openai import OpenAI

# ========== STUDENT-EDITABLE SECTION ==========
TOPIC = "american politics"  # Change this to any topic you're interested in
OPENAI_API_KEY = ""        # Paste your Guardian API key here
GUARDIAN_API_KEY =  ""        # Paste your OpenAI API key here

# ========== SETUP ==========
client = OpenAI(api_key=OPENAI_API_KEY)

# ========== STEP 1: Fetch recent articles from the Guardian's API ==========
def fetch_articles(topic, api_key, num_articles=5):
    url = "https://content.guardianapis.com/search"
    params = {
        "q": topic,
        "order-by": "newest",
        "page-size": num_articles,
        "show-fields": "bodyText",
        "api-key": api_key
    }
    response = requests.get(url, params=params)

    data = response.json()
    results = data.get("response", {}).get("results", [])

    article_data = []
    for item in results:
        title = item.get("webTitle", "")
        url = item.get("webUrl", "")
        body = item.get("fields", {}).get("bodyText", "")
        
        # Get the first paragraph (split by newline)
        first_paragraph = ""
        for paragraph in body.split("\n"):
            if paragraph.strip():
                first_paragraph = paragraph.strip()
                break

        article_data.append({
            "title": title,
            "url": url,
            "first_paragraph": first_paragraph
        })

    return pd.DataFrame(article_data)

# ========== STEP 2: Ask for the student’s question ==========
user_question = input(f"What do you want to know about current events in \"{TOPIC}\"?\n")

# ========== STEP 3: Build prompt and call OpenAI ==========
articles_df = fetch_articles(TOPIC, GUARDIAN_API_KEY)

if articles_df.empty:
    print("No articles found or something went wrong.")
else:
    intro = f"You are analyzing recent articles on the topic: '{TOPIC}'. Here are some summaries:\n\n"
    for i, row in articles_df.iterrows():
        intro += f"Title: {row['title']}\n"
        intro += f"Link: {row['url']}\n"
        intro += f"Summary: {row['first_paragraph']}\n\n"

    full_prompt = intro + f"\nQuestion: {user_question}"

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert news analyst."},
            {"role": "user", "content": full_prompt}
        ]
    )

    response_content = completion.choices[0].message.content
    print("\nThe model returned:\n")
    print(response_content)
