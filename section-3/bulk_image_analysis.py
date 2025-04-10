import pandas as pd
from openai import OpenAI
from tqdm import tqdm


# CSV file containing image details (must have 'image_id' and 'url' columns)
csv_file = "./images.csv"  # Update with your CSV file path if needed

# Read the CSV into a DataFrame
df = pd.read_csv(csv_file)

# Initialize the OpenAI client with your API key
client = OpenAI(api_key="YOUR API KEY HERE")

# List to store the results for each image
results = []

# Iterate over the DataFrame rows with a progress bar
for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing Images"):
    image_id = row["image_id"]
    image_url = row["url"]
    
    # Make the API query that includes both text and image input
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "what's in this image?"},
                {"type": "input_image", "image_url": image_url},
            ],
        }],
    )
    
    # Extract the output text from the response
    output_text = response.output_text
    
    # Append the result for this image
    results.append({
        "image_id": image_id,
        "url": image_url,
        "output_text": output_text,
    })

# Convert the list of dictionaries into a DataFrame
results_df = pd.DataFrame(results)

# Save the results to a CSV file
results_df.to_csv("./images_analysis_results.csv", index=False)

print("Image analysis complete. Results saved to images_analysis_results.csv")
