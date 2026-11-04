from pprint import pprint

from src import tools
from src.tools import PEDIDOS, buscar_produtos, consultar_pedido

print("=== 1) Takamine GD20 ===")
produto = buscar_produtos(nome="Takamine GD20")["produtos"][0]
print(produto["nome"], "| tabela:", produto["preco_tabela"], "| pix:", produto.get("preco_pix"))

print("\n=== 2) Violões em promoção (sem limite de preço) ===")
resultado = buscar_produtos(categoria="Violões", apenas_promocao=True)
for p in resultado["produtos"]:
    print("-", p["nome"], "| de", p["preco_tabela"], "por", p["preco_promocional"], "| pix:", p.get("preco_pix"))

print("\n=== 3) Violões até R$ 1000, só disponíveis ===")
resultado = buscar_produtos(categoria="Violões", preco_maximo=1000, apenas_disponiveis=True)
print("Encontrados:", resultado["total_encontrado"], "| exibindo:", resultado["exibindo"])

print("\n=== 4) Giannini GF-3D (esgotado) ===")
produto = buscar_produtos(nome="Giannini GF-3D")["produtos"][0]
print(produto["nome"], "->", produto["disponibilidade"])

email_certo = PEDIDOS.loc[PEDIDOS["order_id"] == 8, "email"].iloc[0]

print("\n=== 5) Pedido 8: o modelo manda o e-mail certo, mas o cliente NÃO o escreveu ===")
tools.MENSAGENS_CLIENTE.clear()
pprint(consultar_pedido(8, email_certo))

print("\n=== 6) Pedido 8: o cliente escreveu o e-mail ===")
tools.MENSAGENS_CLIENTE.append(f"meu e-mail é {email_certo}")
pprint(consultar_pedido(8, email_certo))

print("\n=== 7) Pedido 8 com o e-mail de OUTRO cliente ===")
tools.MENSAGENS_CLIENTE.append("pedro.oliveira@jmail.com")
pprint(consultar_pedido(8, "pedro.oliveira@jmail.com"))

print("\n=== 8) Prazo de arrependimento calculado ===")
for numero in (1, 8):
    email = PEDIDOS.loc[PEDIDOS["order_id"] == numero, "email"].iloc[0]
    tools.MENSAGENS_CLIENTE.append(email)
    resultado = consultar_pedido(numero, email)
    print(numero, "|", resultado["situacao"], "|", resultado["previsao_entrega"], "|", resultado["prazo_arrependimento"])