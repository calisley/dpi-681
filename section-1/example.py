from openai import OpenAI

client = OpenAI(
    api_key=""
)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": "Write a haiku about bananas."
    }]
)

print(completion.choices[0].message.content)




