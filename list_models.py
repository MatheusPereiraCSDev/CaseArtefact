from google import genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

print(f"Modelo atual no .env: {GEMINI_MODEL}")
print("Modelos disponíveis para gerar texto:\n")

for model in client.models.list():

    if "generateContent" in (model.supported_actions or []):
        print(model.name)