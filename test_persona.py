from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.prompts import build_system_prompt

client = genai.Client(api_key=GEMINI_API_KEY)

config = types.GenerateContentConfig(system_instruction=build_system_prompt())

perguntas = [
    "Oi! Vocês vendem cordas de violão?",
    "Me passa uma receita de bolo de cenoura?",
    "Qual o horário de vocês no sábado?",
    "Posso parcelar uma compra de R$ 900 em quantas vezes?",
    "Você é uma pessoa de verdade?",
]

for pergunta in perguntas:
    resposta = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=pergunta,
        config=config,
    )
    print(f"Cliente: {pergunta}")
    print(f"Téo: {resposta.text}")
    print("-" * 60)