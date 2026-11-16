# loja-mcp — servidor MCP da Loja de Fones

Servidor MCP (Python, [MCP SDK](https://py.sdk.modelcontextprotocol.io/)) via **Streamable HTTP**. Ele expõe a API da loja como tools para agentes de IA. Não guarda dados: cada tool chama a API da loja.

- **API da loja:** https://loja-api-j1g7.onrender.com (docs em `/docs`)
- **Endpoint do MCP (local):** `http://127.0.0.1:8000/mcp`

## Tools

| Tool | Parâmetros | O que faz |
|---|---|---|
| `listar_produtos` | `termo?`, `preco_max?` | Lista produtos, com filtro opcional por nome e preço máximo. Estoque 0 = esgotado. |
| `detalhar_produto` | `produto_id` | Mostra o detalhe de um produto (ex.: `fone-a`). |
| `finalizar_compra` | `produto_id`, `quantidade?` (padrão 1) | Baixa o estoque e devolve o nº do pedido e o total. Se esgotado ou sem estoque suficiente, devolve `{"sucesso": false, "erro": "..."}`. |
| `resetar_estoques` | — | Restaura estoques e numeração de pedidos (para demonstrações). |

## Como rodar

Pré-requisito: Python 3.11+.

```bash
cd mcp-loja
python -m venv .venv
.venv\Scripts\activate          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

Aponte para a API publicada e suba o servidor:

```powershell
# PowerShell
$env:LOJA_API_URL="https://loja-api-j1g7.onrender.com"
python app.py
```

```bash
# Linux/Mac
LOJA_API_URL=https://loja-api-j1g7.onrender.com python app.py
```

Sem `LOJA_API_URL`, ele usa a API local `http://127.0.0.1:8001`. O servidor roda até `Ctrl+C`, e cada chamada aparece no terminal, por exemplo `[finalizar_compra] id='fone-a' qtd=1`.

> A API está no plano gratuito do Render e dorme quando fica parada: a primeira chamada pode levar cerca de 1 minuto.

## Testar no Inspector (precisa de Node.js)

Listar as tools:

```bash
npx -y @modelcontextprotocol/inspector --cli http://127.0.0.1:8000/mcp --method tools/list
```

Chamar uma tool:

```bash
npx -y @modelcontextprotocol/inspector --cli http://127.0.0.1:8000/mcp --method tools/call --tool-name listar_produtos --tool-arg preco_max=200
```

Interface visual: `npx -y @modelcontextprotocol/inspector`, depois **Transport = Streamable HTTP**, URL `http://127.0.0.1:8000/mcp` e **Connect**.

## Usar no opencode

Crie ou edite o `opencode.json` do projeto (ou `~/.config/opencode/opencode.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "loja-mcp": {
      "type": "remote",
      "url": "http://127.0.0.1:8000/mcp",
      "enabled": true
    }
  }
}
```

Com o servidor rodando, abra o opencode e peça, por exemplo:

> Liste os fones até R$ 200 e compre uma unidade do mais barato.

## Observações

- Não renomeie `app.py` para `mcp.py`: o nome sombreia o pacote `mcp`.
- Sem autenticação e só em `127.0.0.1`: não exponha na internet sem colocar auth na frente.
- Os dados da API ficam em memória: reiniciar a API restaura os estoques.
