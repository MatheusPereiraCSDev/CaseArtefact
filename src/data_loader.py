import json

import pandas as pd
from pypdf import PdfReader

from src.config import DATA_DIR

STATUS_PEDIDO_PT = {
    "pending": "pendente (aguardando confirmação)",
    "confirmed": "confirmado (em preparação)",
    "shipped": "enviado",
    "delivered": "entregue",
    "cancelled": "cancelado",
}

PAGAMENTO_PT = {
    "pix": "PIX",
    "debit": "cartão de débito",
    "boleto": "boleto bancário",
    "credit_3x": "cartão de crédito em 3x",
    "credit_6x": "cartão de crédito em 6x",
    "credit_12x": "cartão de crédito em 12x",
}

DESCONTO_PIX = 5 


def _converter_specs(texto):
    """Transforma o texto JSON da coluna specs em dicionário."""
    try:
        return json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        return {} 


def load_products() -> pd.DataFrame:
    """Produtos já com categoria, promoção ativa, preços finais e disponibilidade."""
    produtos = pd.read_csv(DATA_DIR / "products.csv")

    categorias = pd.read_csv(DATA_DIR / "categories.csv")
    categorias = categorias.rename(columns={"name": "category_name"})
    categorias = categorias[["category_id", "category_name"]]

    promocoes = pd.read_csv(DATA_DIR / "promotions.csv")
    promocoes = promocoes[promocoes["is_active"] == 1]
    promocoes = promocoes.rename(columns={"description": "promo_name"})
    promocoes = promocoes[["product_id", "discount_percent", "promo_name"]]
    promocoes = promocoes.drop_duplicates(subset="product_id") 

    df = produtos.merge(categorias, on="category_id", how="left")
    df = df.merge(promocoes, on="product_id", how="left")

    df["specs"] = df["specs"].apply(_converter_specs)
    df["has_promo"] = df["discount_percent"].notna()

    desconto = df["discount_percent"].fillna(0)
    df["final_price_brl"] = (df["price_brl"] * (1 - desconto / 100)).round(2)

    preco_pix = (df["price_brl"] * (1 - DESCONTO_PIX / 100)).round(2)
    df["pix_price_brl"] = preco_pix.where(~df["has_promo"])

    df["available"] = (df["status"] == "active") & (df["stock_quantity"] > 0)

    return df


def load_orders() -> pd.DataFrame:
    """Pedidos já com nome do cliente, itens e textos em português."""
    pedidos = pd.read_csv(
        DATA_DIR / "orders.csv",
        parse_dates=["order_date", "estimated_delivery"],
    )

    clientes = pd.read_csv(DATA_DIR / "customers.csv")
    clientes = clientes.rename(columns={"name": "customer_name"})
    clientes = clientes[["customer_id", "customer_name", "email", "phone"]]

    produtos = pd.read_csv(DATA_DIR / "products.csv")[["product_id", "name"]]
    produtos = produtos.rename(columns={"name": "product_name"})
    itens = pd.read_csv(DATA_DIR / "order_items.csv").merge(produtos, on="product_id")

    itens_por_pedido = {}
    for linha in itens.itertuples():
        itens_por_pedido.setdefault(linha.order_id, []).append(
            {"product_name": linha.product_name, "quantity": linha.quantity}
        )

    df = pedidos.merge(clientes, on="customer_id", how="left")
    df["items"] = df["order_id"].map(itens_por_pedido)
    df["status_pt"] = df["status"].map(STATUS_PEDIDO_PT)
    df["payment_pt"] = df["payment_method"].map(PAGAMENTO_PT)

    return df


def load_policies() -> str:
    """Extrai o texto completo do manual de políticas (PDF)."""
    leitor = PdfReader(DATA_DIR / "politicas_da_loja.pdf")
    paginas = [pagina.extract_text() for pagina in leitor.pages]
    return "\n\n".join(paginas)