from openai import OpenAI
import json
import requests
import matplotlib.pyplot as plt
import pandas as pd

GUARDIAN_API_KEY = ""  # Replace with your Guardian API key

client = OpenAI(
    api_key=""
)

###### Defining real functions for US to exectute ######
def get_news_articles(query: str, order_by: str, page_size: int, output_path: str) -> str:
    url = "https://content.guardianapis.com/search"
    params = {
        "q": query,
        "order-by": order_by,
        "page-size": page_size,
        "show-fields": "bodyText",
        "api-key": GUARDIAN_API_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    results = data.get("response", {}).get("results", [])

    articles = []
    for item in results:
        fields = item.get("fields", {})
        body = fields.get("bodyText", "")
        date = item.get("webPublicationDate", "")
        articles.append({"date": date, "article_text": body})

    df = pd.DataFrame(articles)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Saved {len(df)} articles to {output_path}")
    return df


def get_weather(latitude, longitude):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    return data['current']['temperature_2m']

def analyze_sentiment(sentiments, output_path):
    try:
        df = pd.DataFrame(sentiments)

        if not all(1 <= s <= 10 for s in df["sentiment"]):
            return "Error: Sentiment scores must be between 1 and 10."

        df.to_csv(output_path, index=False, encoding="utf-8")
 
        print(f"Saved sentiment analysis to {output_path}")
        return f"Saved sentiment analysis to {output_path}"
    except Exception as e:
        return f"Error saving sentiment output: {str(e)}"
    
def graph_data(csv_path: str, x_column: str, y_column: str, title: str, x_label: str, y_label: str) -> str:
    try:
        df = pd.read_csv(csv_path)

        if x_column not in df.columns or y_column not in df.columns:
            return f"Error: Columns '{x_column}' and/or '{y_column}' not found in {csv_path}."

        # Convert date to full datetime
        df[x_column] = pd.to_datetime(df[x_column], errors='coerce')
        df = df.dropna(subset=[x_column, y_column])
        df = df.sort_values(by=x_column)

        # Plot each entry (no aggregation)
        plt.figure(figsize=(12, 6))
        plt.plot(df[x_column], df[y_column], marker='o', linestyle='-', alpha=0.7)

        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        output_image_path = csv_path.replace(".csv", "_graph.png")
        plt.savefig(output_image_path)
        plt.close()

        return f"Graph saved to {output_image_path}"
    
    except Exception as e:
        return f"Graphing error: {str(e)}"



###### Model's version of the functions ######

tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "string",
                    "description": "Latitude of desired location"
                },
                "longitude": {
                    "type": "string",
                    "description": "Longitude of desired location"
                }
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_news_articles",
        "description": "Fetch news articles from The Guardian API and save them to a CSV.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query, e.g., 'climate change'"
                },
                "order_by": {
                    "type": "string",
                    "enum": ["newest", "oldest", "relevance"],
                    "description": "How to sort the articles"
                },
                "page_size": {
                    "type": "integer",
                    "description": "How many articles to return (max 200)"
                },
                "output_path": {
                    "type": "string",
                    "description": "File path where the articles will be saved as CSV"
                }
            },
            "required": ["query", "order_by", "page_size", "output_path"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "analyze_sentiment",
        "description": "Analyze sentiment of article texts on a scale from 1 (negative) to 10 (positive), and save results as a CSV.",
        "parameters": {
            "type": "object",
            "properties": {
                "sentiments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "datetime": {"type": "string"},
                            "sentiment": {
                                "type": "integer",
                                "enum": [1,2,3,4,5,6,7,8,9,10],
                                "description": "Sentiment score: 1 (very negative) to 10 (very positive)"
                            }
                        },
                        "required": ["datetime",  "sentiment"],
                        "additionalProperties": False  
                    },
                    "description": "Each entry contains the article snippet, datetime, and its sentiment score. Do NOT change the datetimes."
                },
                "output_path": {
                    "type": "string",
                    "description": "CSV file path to save sentiment results"
                }
            },
            "required": ["sentiments", "output_path"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "graph_data",
        "description": "Generate a graph from a CSV file.",
        "parameters": {
            "type": "object",
            "properties": {
                "csv_path": {
                    "type": "string",
                    "description": "Path to the CSV file containing the data"
                },
                "x_column": {
                    "type": "string",
                    "description": "Column name to use as x-axis"
                },
                "y_column": {
                    "type": "string",
                    "description": "Column name to use as y-axis"
                },
                "title": {
                    "type": "string",
                    "description": "Title of the graph"
                },
                "x_label": {
                    "type": "string",
                    "description": "Label for the x-axis"
                },
                "y_label": {
                    "type": "string",
                    "description": "Label for the y-axis"
                }
            },
            "required": ["csv_path", "x_column", "y_column", "title", "x_label", "y_label"],
            "additionalProperties": False
        }
    }
]


# General function for calling our functions
def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)
    elif name == "get_news_articles":
        return get_news_articles(**args)
    elif name == "graph_data":
        return graph_data(**args)
    elif name == "analyze_sentiment":
        return analyze_sentiment(**args)
    else:
        return f"No such function: {name}"


###### UI ###### 

# Step 2: Get user input
user_query = input("Ask the agent something: ")
messages = [{"role": "user", "content": user_query}]

while True:
    response = client.responses.create(
        model="gpt-4.1",
        input=messages,
        tools=tools
    )
    output = response.output

    if output and output[0].type == "function_call":
        tool_call = output[0]
        print(f"\nTool call detected: {tool_call.name}")
        args = json.loads(tool_call.arguments)

        result = call_function(tool_call.name, args)




        if isinstance(result, dict):
            result = json.dumps(result)

        # Append both the call and the result
        messages.append(tool_call.model_dump())

        messages.append({
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": str(result)
        })

    else:
        print("\nAgent response:\n")
        print(response.output_text)
        break