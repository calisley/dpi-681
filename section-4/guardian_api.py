import requests
import uuid
import csv

def fetch_guardian_articles(api_key):
    url = "https://content.guardianapis.com/search"
    params = {
        "q": "american politics",
        "order-by": "newest",
        "page-size": 20,
        "show-fields": "bodyText",
        "api-key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        articles = data.get("response", {}).get("results", [])
        return articles
    else:
        print(f"Error: Received status code {response.status_code}")
        return []

def extract_first_paragraph(body_text):
    # Split the body text by newline characters.
    # Assumes paragraphs are separated by one or more newline characters.
    paragraphs = [p.strip() for p in body_text.split("\n") if p.strip()]
    return paragraphs[0] if paragraphs else ""

def extract_articles_data(articles):
    articles_data = []
    for article in articles:
        # Generate a random unique identifier for each article
        article_id = str(uuid.uuid4())
        # Extract the first paragraph from the 'bodyText' field
        full_text = article.get("fields", {}).get("bodyText", "")
        first_paragraph = extract_first_paragraph(full_text)
        articles_data.append({
            "id": article_id,
            "article_text": first_paragraph
        })
    return articles_data

def save_to_csv(articles_data, filename="articles.csv"):
    # Write articles data to a CSV file with columns: id and article_text
    with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["id", "article_text"])
        writer.writeheader()
        for data in articles_data:
            writer.writerow(data)
    print(f"Data successfully saved to {filename}")

if __name__ == "__main__":
    API_KEY = ""  # Replace with your actual Guardian API key
    articles = fetch_guardian_articles(API_KEY)
    if articles:
        articles_data = extract_articles_data(articles)
        save_to_csv(articles_data)
    else:
        print("No articles found or an error occurred.")
