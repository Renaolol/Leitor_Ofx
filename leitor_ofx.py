from ofxparse import OfxParser
import streamlit as st
import pandas as pd


def formata_valor(value):
    value = f'{value:,.2f}'
    return "R$ " + value.replace(",", "X").replace(".", ",").replace("X", ".")


def normaliza_historico(memo):
    if memo is None:
        return "(Sem histórico)"
    memo = str(memo).strip()
    return memo if memo else "(Sem histórico)"


def historicos_selecionados(historicos, key_prefix):
    selecionados = []
    for historico in historicos:
        checkbox_key = f"{key_prefix}_{historico}"
        if st.checkbox(historico, key=checkbox_key):
            selecionados.append(historico)
    return selecionados

st.title("Leitor de OFX -- Entradas")
ofx_file = st.file_uploader("Anexe o OFX", ".ofx", False)
if ofx_file is not None:
    ofx = OfxParser.parse(ofx_file)

    account = ofx.account
    statement = account.statement
    lista_transacoes = []
    for transaction in statement.transactions:
        lista_transacoes.append(
            [
                transaction.type,
                transaction.date,
                transaction.amount,
                normaliza_historico(transaction.memo),
            ]
        )

    df = pd.DataFrame(lista_transacoes, columns=["Tipo", "Data", "Valor", "Histórico"])
    df_creditos = df[df["Tipo"] == "credit"]
    df_debitos = df[df["Tipo"] == "debit"]

    historicos_credito = sorted(df_creditos["Histórico"].dropna().unique(), key=str.lower)
    historicos_debito = sorted(df_debitos["Histórico"].dropna().unique(), key=str.lower)

    col_tabela, col_filtros = st.columns([2, 1])

    with col_tabela:
        st.dataframe(df)

    with col_filtros:
        st.subheader("Históricos de Entradas")
        selecionados_credito = historicos_selecionados(historicos_credito, "credito")

        st.subheader("Históricos de Saídas")
        selecionados_debito = historicos_selecionados(historicos_debito, "debito")

    total_creditos = (
        df_creditos[df_creditos["Histórico"].isin(selecionados_credito)]["Valor"].sum()
        if selecionados_credito
        else df_creditos["Valor"].sum()
    )
    total_debitos = (
        df_debitos[df_debitos["Histórico"].isin(selecionados_debito)]["Valor"].sum()
        if selecionados_debito
        else df_debitos["Valor"].sum()
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Entradas", formata_valor(total_creditos))
    with col2:
        st.metric("Total de Saídas", formata_valor(total_debitos))
