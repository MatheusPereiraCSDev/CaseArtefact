import unicodedata
import pandas as pd

from src.data_loader import load_orders, load_products

PRODUTOS = load_products()
PEDIDOS = load_orders()

MAX_RESULTADOS = 8  


def _normalizar(texto) -> str:
    """Minúsculas e sem acento: 'Violões' -> 'violoes'. Facilita a busca."""
    decomposto = unicodedata.normalize("NFD", str(texto))
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return sem_acento.lower().strip()


def _disponibilidade(status: str, estoque: int) -> str:
    """Traduz status + estoque em um texto claro para o atendimento."""
    if status == "discontinued":
        return "descontinuado (não faz mais parte do catálogo)"
    if status == "coming_soon":
        return "em breve (ainda não disponível para compra)"
    if estoque <= 0:
        return "esgotado no momento"
    return "disponível"


def _ou_none(valor):
    """Troca valores vazios do pandas (NaN/NaT) por None."""
    return None if pd.isna(valor) else valor


def buscar_produtos(
    nome: str = "",
    categoria: str = "",
    preco_maximo: float = 0,
    apenas_disponiveis: bool = False,
) -> dict:
    """Busca instrumentos musicais no catálogo da loja e retorna preço, promoção e disponibilidade.

    Use SEMPRE que o cliente perguntar sobre preço, estoque, disponibilidade,
    características ou quiser opções de instrumentos. Nunca responda sobre
    preço ou estoque sem chamar esta função.

    Args:
        nome: Nome ou parte do nome do produto, como 'Takamine GD20' ou 'Yamaha'.
            Deixe vazio para não filtrar por nome.
        categoria: Categoria do instrumento. Use exatamente um destes valores:
            'Guitarras', 'Baixos', 'Baterias e Percussão', 'Teclados e Pianos',
            'Violões', 'Instrumentos de Sopro (Madeiras)',
            'Instrumentos de Sopro (Metais)', 'Cordas Orquestrais', 'Ukuleles'.
            Deixe vazio para não filtrar por categoria.
        preco_maximo: Preço máximo em reais que o cliente quer pagar (considera o
            preço já com promoção). Use 0 para não limitar.
        apenas_disponiveis: Use True quando o cliente quer opções para comprar.
            Use False quando ele pergunta por um produto específico, para poder
            informar se está esgotado ou descontinuado.

    Returns:
        Dicionário com a lista de produtos encontrados e seus dados.
    """
    
    mascara = pd.Series(True, index=PRODUTOS.index)

    if nome:
        nomes = PRODUTOS["name"].apply(_normalizar)
        for palavra in _normalizar(nome).split():
            mascara &= nomes.str.contains(palavra, regex=False)

    if categoria:
        categorias = PRODUTOS["category_name"].apply(_normalizar)
        mascara &= categorias.str.contains(_normalizar(categoria), regex=False)

    if preco_maximo > 0:
        mascara &= PRODUTOS["final_price_brl"] <= preco_maximo

    if apenas_disponiveis:
        mascara &= PRODUTOS["available"]

    encontrados = PRODUTOS[mascara]
    encontrados = encontrados.sort_values(
        by=["available", "final_price_brl"], ascending=[False, True]
    )

    if encontrados.empty:
        return {"total_encontrado": 0, "produtos": [], "mensagem": "Nenhum produto encontrado."}

    produtos = []
    for p in encontrados.head(MAX_RESULTADOS).itertuples():
        item = {
            "nome": p.name,
            "categoria": p.category_name,
            "descricao": p.description,
            "especificacoes": p.specs,
            "disponibilidade": _disponibilidade(p.status, p.stock_quantity),
            "unidades_em_estoque": int(p.stock_quantity),
            "preco_tabela": float(p.price_brl),
            "em_promocao": bool(p.has_promo),
        }
        if p.has_promo:
            item["promocao"] = p.promo_name
            item["desconto_percentual"] = int(p.discount_percent)
            item["preco_promocional"] = float(p.final_price_brl)
        
        else:
            item["preco_pix"] = float(p.pix_price_brl)
        produtos.append(item)

    return {
        "total_encontrado": len(encontrados),
        "exibindo": len(produtos),
        "produtos": produtos,
    }


def consultar_pedido(numero_pedido: int, email_cliente: str) -> dict:
    """Consulta o status de um pedido (situação, itens, rastreio e previsão de entrega).

    Use quando o cliente perguntar sobre o andamento, rastreio ou entrega de um
    pedido. É OBRIGATÓRIO ter o número do pedido E o e-mail cadastrado do cliente;
    se faltar algum, peça ao cliente antes de chamar esta função.

    Args:
        numero_pedido: Número do pedido informado pelo cliente.
        email_cliente: E-mail cadastrado do cliente, usado para confirmar a identidade.

    Returns:
        Dicionário com os dados do pedido, ou uma mensagem de erro se os dados não conferirem.
    """
    erro = {
        "erro": "Não encontrei um pedido com esses dados. "
        "Peça ao cliente para conferir o número do pedido e o e-mail do cadastro."
    }

    pedido = PEDIDOS[PEDIDOS["order_id"] == int(numero_pedido)]
    if pedido.empty:
        return erro

    p = pedido.iloc[0]
    
    if _normalizar(p["email"]) != _normalizar(email_cliente):
        return erro

    previsao = _ou_none(p["estimated_delivery"])

    return {
        "numero_pedido": int(p["order_id"]),
        "cliente": p["customer_name"],
        "data_pedido": p["order_date"].strftime("%d/%m/%Y"),
        "situacao": p["status_pt"],
        "itens": p["items"],
        "total": float(p["total_brl"]),
        "forma_pagamento": p["payment_pt"],
        "codigo_rastreio": _ou_none(p["tracking_code"]),
        "previsao_entrega": previsao.strftime("%d/%m/%Y") if previsao is not None else None,
        "observacoes": _ou_none(p["notes"]),
    }