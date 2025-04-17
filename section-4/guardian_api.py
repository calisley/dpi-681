import requests
import pandas as pd
from dotenv import load_dotenv

API_KEY = ""  # Replace with your Guardian API key

def fetch_articles(api_key):
    url = "https://content.guardianapis.com/search"
    params = {
        "q": "american politics",         # This is the search query. You can change it to any topic (e.g., "climate change", "technology").
        "order-by": "newest",             # Controls article sorting. Options: "newest", "oldest", or "relevance".
        "page-size": 20,                  # Number of articles to return. Max is 200. You can adjust this live to show more or fewer.
        "show-fields": "bodyText",        # Tells the API what extra fields to return. Other options: "headline", "trailText", "thumbnail", etc.
        "api-key": api_key                
    }
    response = requests.get(url, params=params)

    data = response.json()
    results = data.get("response", {}).get("results", [])

    article_texts = []
    for item in results:
        fields = item.get("fields", {})
        #I wanted the body text, but we can get anything else we want!
        body = fields.get("bodyText", "")
        article_texts.append({"article_text": body})

    return pd.DataFrame(article_texts)

if __name__ == "__main__":
    df = fetch_articles(API_KEY)
    
    df.to_csv("articles.csv", index=False, encoding="utf-8")
    print("Saved to articles.csv")
