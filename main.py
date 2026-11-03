import sys

from src.agent import EmporioAgent

DEBUG = "--debug" in sys.argv


def main():
    agente = EmporioAgent()

    print("=" * 60)
    print("Empório da Música - atendimento (digite 'sair' para encerrar)")
    print("=" * 60)
    print("Téo: Oi! Aqui é o Téo, assistente virtual da Empório da Música. Como posso ajudar?")

    while True:
        mensagem = input("\nVocê: ").strip()

        if not mensagem:
            continue
        if mensagem.lower() in ("sair", "exit", "quit"):
            print("Téo: Valeu pelo papo! Qualquer coisa, é só chamar. 🎶")
            break

        resposta = agente.responder(mensagem)

        if DEBUG:
            for nome, argumentos in agente.ferramentas_usadas():
                print(f"  [ferramenta] {nome}({argumentos})")

        print(f"\nTéo: {resposta}")


if __name__ == "__main__":
    main()