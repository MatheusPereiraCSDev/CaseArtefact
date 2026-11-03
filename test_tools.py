from pprint import pprint

from src.tools import PEDIDOS, buscar_produtos, consultar_pedido

print("=== 1) Produto específico ===")
pprint(buscar_produtos(nome="Takamine GD20"))

print("\n=== 2) Violões até R$ 1000, só disponíveis ===")
resultado = buscar_produtos(categoria="Violões", preco_maximo=1000, apenas_disponiveis=True)
print("Encontrados:", resultado["total_encontrado"])
for p in resultado["produtos"]:
    print("-", p["nome"], "| tabela:", p["preco_tabela"], "| promoção:", p["em_promocao"])

print("\n=== 3) Produto esgotado (Giannini GF-3D) ===")
resultado = buscar_produtos(nome="Giannini GF-3D")
print(resultado["produtos"][0]["nome"], "->", resultado["produtos"][0]["disponibilidade"])

print("\n=== 4) Pedido 8 com e-mail correto ===")
email_certo = PEDIDOS.loc[PEDIDOS["order_id"] == 8, "email"].iloc[0]
pprint(consultar_pedido(8, email_certo))

print("\n=== 5) Pedido 8 com e-mail errado ===")
pprint(consultar_pedido(8, "outra.pessoa@jmail.com"))