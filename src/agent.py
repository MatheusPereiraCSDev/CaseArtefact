import time

from google import genai
from google.genai import errors, types

from src import tools
from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.prompts import build_system_prompt

MAX_TENTATIVAS = 4
ERROS_TEMPORARIOS = (429, 500, 503) 

MENSAGEM_INDISPONIVEL = (
    "Poxa, estou com uma instabilidade aqui no momento. 😕 "
    "Tenta de novo em alguns instantes ou fale com a nossa equipe "
    "pelo WhatsApp (67) 3341-4444."
)


class EmporioAgent:
    """Agente de atendimento da Empório da Música (uma conversa por instância)."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.client = genai.Client(api_key=GEMINI_API_KEY)

        config = types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
            tools=[tools.buscar_produtos, tools.consultar_pedido],
            temperature=0.3,
        )

        self.chat = self.client.chats.create(model=GEMINI_MODEL, config=config)

        tools.MENSAGENS_CLIENTE.clear()  # NOVO

    def responder(self, mensagem: str) -> str:
        """Envia a mensagem do cliente e devolve a resposta do Téo."""
        tools.CHAMADAS.clear()
        tools.MENSAGENS_CLIENTE.append(mensagem)  

        for tentativa in range(1, MAX_TENTATIVAS + 1):
            try:
                resposta = self.chat.send_message(mensagem)
                return resposta.text or MENSAGEM_INDISPONIVEL
            except errors.APIError as erro:
                
                if erro.code not in ERROS_TEMPORARIOS:
                    raise

                if self.debug:
                    print(
                        f"  [aviso] erro {erro.code} da API "
                        f"(tentativa {tentativa}/{MAX_TENTATIVAS})"
                    )

                if tentativa == MAX_TENTATIVAS:
                    return MENSAGEM_INDISPONIVEL
                time.sleep(2**tentativa)  

    def ferramentas_usadas(self) -> list:
        """Ferramentas chamadas durante a última mensagem."""
        return list(tools.CHAMADAS)