from google import genai
from google.genai import errors

from src.config import GEMINI_API_KEY

CANDIDATOS = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
]

client = genai.Client(api_key=GEMINI_API_KEY)

for modelo in CANDIDATOS:
    try:
        resposta = client.models.generate_content(
            model=modelo,
            contents="Responda apenas: ok",
        )
        print(f"OK   {modelo} -> {resposta.text.strip()[:30]}")
    except errors.APIError as erro:
        print(f"ERRO {modelo} -> {erro.code} {getattr(erro, 'status', '')}")