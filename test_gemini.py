from google import genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents="Cumprimente um cliente em uma frase, como atendente de uma loja de instrumentos musicais.",
)

print(response.text)