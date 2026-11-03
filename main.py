import sys
from datetime import datetime
from pathlib import Path

from src.agent import EmporioAgent

DEBUG = "--debug" in sys.argv
SAUDACAO = "Oi! Aqui é o Téo, assistente virtual da Empório da Música. Como posso ajudar?"


def _arquivo_de_saida():
    """Se o comando tiver '--salvar nome', devolve o caminho exemplos/nome.md."""
    if "--salvar" in sys.argv:
        indice = sys.argv.index("--salvar")
        if indice + 1 < len(sys.argv):
            pasta = Path(__file__).resolve().parent / "exemplos"
            pasta.mkdir(exist_ok=True)
            return pasta / f"{sys.argv[indice + 1]}.md"
    return None


def main():
    agente = EmporioAgent(debug=DEBUG)
    saida = _arquivo_de_saida()
    registro = [f"**Téo:** {SAUDACAO}\n"]  # linhas que irão para o arquivo .md

    print("=" * 60)
    print("Empório da Música - atendimento (digite 'sair' para encerrar)")
    print("=" * 60)
    print(f"Téo: {SAUDACAO}")

    try:
        while True:
            try:
                mensagem = input("\nVocê: ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not mensagem:
                continue
            if mensagem.lower() in ("sair", "exit", "quit"):
                print("Téo: Valeu pelo papo! Qualquer coisa, é só chamar. 🎶")
                break

            resposta = agente.responder(mensagem)
            usadas = agente.ferramentas_usadas()

            if DEBUG:
                for nome, argumentos in usadas:
                    print(f"  [ferramenta] {nome}({argumentos})")
            print(f"\nTéo: {resposta}")

            registro.append(f"**Cliente:** {mensagem}\n")
            for nome, argumentos in usadas:
                registro.append(f"> 🔧 *Consulta ao sistema:* `{nome}({argumentos})`\n")
            registro.append(f"**Téo:** {resposta}\n")
    finally:
        # Só salva se o cliente chegou a mandar alguma mensagem
        if saida and len(registro) > 1:
            cabecalho = f"# Conversa: {saida.stem}\n\n_Gerada em {datetime.now():%d/%m/%Y %H:%M}_\n\n---\n\n"
            saida.write_text(cabecalho + "\n".join(registro), encoding="utf-8")
            print(f"\nConversa salva em {saida}")


if __name__ == "__main__":
    main()