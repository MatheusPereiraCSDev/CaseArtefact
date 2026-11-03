from src.data_loader import load_orders, load_policies, load_products

produtos = load_products()
pedidos = load_orders()
politicas = load_policies()

print(f"Produtos: {len(produtos)} | Pedidos: {len(pedidos)}")
print(f"Produtos disponíveis: {produtos['available'].sum()}")
print()

print("--- Takamine GD20 ---")
gd20 = produtos[produtos["name"].str.contains("GD20")]
print(gd20[["name", "price_brl", "pix_price_brl", "stock_quantity", "available"]].to_string())
print()

print("--- Produtos em promoção ativa ---")
promo = produtos[produtos["has_promo"]]
print(promo[["name", "price_brl", "discount_percent", "final_price_brl", "pix_price_brl"]].to_string())
print()

print("--- Pedido 8 ---")
pedido = pedidos[pedidos["order_id"] == 8].iloc[0]
print(pedido["customer_name"], "|", pedido["status_pt"], "|", pedido["tracking_code"])
print(pedido["items"])
print()

print("--- Políticas (início do texto) ---")
print(f"Total de caracteres: {len(politicas)}")
print(politicas[:300])