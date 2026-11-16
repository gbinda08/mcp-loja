"""Servidor MCP da loja — expõe a API da loja como tools para agentes de IA.

Rodar:
    pip install -r requirements.txt
    python app.py
Sobe em http://127.0.0.1:8000/mcp

A URL da API vem da variável LOJA_API_URL (padrão: API local na porta 8001).
"""

import os

import httpx
from mcp.server.mcpserver import MCPServer

API_URL = os.environ.get("LOJA_API_URL", "http://127.0.0.1:8001").rstrip("/")

mcp = MCPServer("loja-mcp")


def _chamar(metodo: str, caminho: str, **kwargs):
    """Chama a API e transforma erros HTTP em mensagens legíveis para o agente."""
    r = httpx.request(metodo, API_URL + caminho, timeout=90, **kwargs)
    if r.status_code >= 400:
        try:
            detalhe = r.json().get("detail", r.text)
        except Exception:
            detalhe = r.text
        # Devolve como resposta normal: o SDK esconde o texto de exceções do agente.
        return {"sucesso": False, "erro": detalhe}
    return r.json()


@mcp.tool()
def listar_produtos(termo: str | None = None, preco_max: float | None = None) -> list[dict]:
    """Lista os produtos da loja. Filtra pelo nome (termo) e/ou preço máximo, ambos opcionais.
    Cada produto traz id, nome, preço, estoque e descrição. Estoque 0 significa esgotado."""
    print(f"[listar_produtos] termo={termo!r} preco_max={preco_max}", flush=True)
    produtos = _chamar("GET", "/produtos")
    if termo:
        produtos = [p for p in produtos if termo.strip().lower() in p["nome"].lower()]
    if preco_max is not None:
        produtos = [p for p in produtos if p["preco"] <= preco_max]
    return produtos


@mcp.tool()
def detalhar_produto(produto_id: str) -> dict:
    """Mostra o detalhe de um produto a partir do seu id (ex.: 'fone-a')."""
    print(f"[detalhar_produto] id={produto_id!r}", flush=True)
    return _chamar("GET", f"/produtos/{produto_id}")


@mcp.tool()
def finalizar_compra(produto_id: str, quantidade: int = 1) -> dict:
    """Compra um produto: baixa o estoque e devolve o número do pedido e o total.
    Falha se o produto estiver esgotado ou não houver estoque suficiente."""
    print(f"[finalizar_compra] id={produto_id!r} qtd={quantidade}", flush=True)
    return _chamar("POST", "/compras", json={"itens": [{"id": produto_id, "quantidade": quantidade}]})


@mcp.tool()
def resetar_estoques() -> dict:
    """Restaura os estoques e a numeração de pedidos ao estado inicial (uso em demonstrações)."""
    print("[resetar_estoques]", flush=True)
    return _chamar("POST", "/admin/reset")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
