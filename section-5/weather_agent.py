from openai import OpenAI
import json
import requests

client = OpenAI(
    api_key=""
)

tools = [{
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
        "required": ["latitude","longitude"],
        "additionalProperties": False
    }
}]

def get_weather(latitude, longitude):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    return data['current']['temperature_2m']

# Step 2: Get user input
user_query = input("Ask the agent anything (weather or unrelated): ")
messages = [{"role": "user", "content": user_query}]

while True:
    response = client.responses.create(model="gpt-4.1", input=messages, tools=tools)
    output = response.output

    if output and output[0].type == "function_call":
        print("Tool call detected!")
        tool_call = output[0]
        args = json.loads(tool_call.arguments)
        result = get_weather(**args)

        # Append the tool call + output
        messages.append(tool_call.model_dump())
        messages.append({
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": str(result)
        })

    else:
        print(response.output_text)
        break
