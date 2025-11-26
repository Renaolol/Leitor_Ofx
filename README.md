# Leitor OFX

Aplicativo simples em Streamlit para visualizar arquivos bancários `.ofx`. O app lê o extrato, lista as transações e apresenta métricas de entradas e saídas em reais.

## Requisitos

- Python 3.10+ (testado no Streamlit)
- Dependências: `streamlit`, `ofxparse`, `pandas`

Instale tudo em um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install streamlit ofxparse pandas
```

## Como executar

```bash
streamlit run leitor_ofx.py  # usa a porta padrao 8501
# ou respeitando .streamlit/config.toml (porta 8000):
streamlit run leitor_ofx.py --server.port 8000
```

Abra o endereço indicado no terminal (ex.: http://localhost:8000).

## Uso

1) Clique em **Anexe o OFX** e selecione um arquivo `.ofx`.  
2) A tabela exibira tipo, data, valor (formatado em R$) e historico.  
3) Os cards mostram os totais de entradas (creditos) e saidas (debitos).

## Estrutura

- `leitor_ofx.py`: app Streamlit que faz upload, parsing via OfxParser e exibicao das transacoes.
- `.streamlit/config.toml`: configura a porta do servidor (8000).
- `LICENSE`: licenca MIT.

## Notas e personalizacao

- Para mudar a porta, edite `.streamlit/config.toml` ou passe `--server.port`.
- Para adicionar campos do OFX (ex.: saldo), amplie a lista `lista_transacoes` em `leitor_ofx.py`.

## Licenca

MIT License. Veja `LICENSE` para detalhes.
