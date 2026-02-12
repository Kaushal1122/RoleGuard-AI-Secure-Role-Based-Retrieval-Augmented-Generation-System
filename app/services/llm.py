import os
from groq import Groq

# Initialize Groq client using environment variable
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(prompt: str):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300
        )

        return completion.choices[0].message.content.strip()

    except Exception:
        return "I don't know"
