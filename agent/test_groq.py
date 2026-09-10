import os
from dotenv import load_dotenv
#from groq import Groq
from google import genai

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY tidak ditemukan")

#client = Groq(api_key=api_key)
client = genai.Client(api_key=api_key)

#response = client.chat.completions.create(
response = client.models.generate_content(
    model="gemini-3.8-flash",
    messages=[
        {
            "role": "user",
            "content": "Jawab singkat dalam Bahasa Indonesia: apakah koneksi berhasil?"
        }
    ]
)

print(response.choices[0].message.content)