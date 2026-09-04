from decimal import Decimal, InvalidOperation
from io import StringIO
import re

import pandas as pd
import streamlit as st
from ofxparse import OfxParser


st.set_page_config(page_title="Leitor de OFX", layout="wide")

AMOUNT_TAG_PATTERN = re.compile(r"(<[A-Z0-9_.-]*AMT>)([^<\r\n]+)", re.IGNORECASE)
CHARSET_PATTERN = re.compile(r"(?im)^CHARSET:\s*([^\r\n]+)")


def detecta_encodings_ofx(conteudo):
    cabecalho = conteudo[:4096].decode("ascii", errors="ignore")
    charset_match = CHARSET_PATTERN.search(cabecalho)

    encodings = []
    if charset_match:
        charset = charset_match.group(1).strip().upper()
        mapa_charsets = {
            "1252": "cp1252",
            "437": "cp437",
            "65001": "utf-8",
            "ANSI": "cp1252",
            "USASCII": "ascii",
            "UTF-8": "utf-8",
            "UTF8": "utf-8",
            "WINDOWS-1252": "cp1252",
            "ISO-8859-1": "latin-1",
            "8859-1": "latin-1",
            "LATIN1": "latin-1",
            "NONE": "latin-1",
        }
        encodings.append(mapa_charsets.get(charset, charset.lower()))

    encodings.extend(["utf-8", "cp1252", "latin-1"])

    encodings_unicos = []
    for encoding in encodings:
        if encoding not in encodings_unicos:
            encodings_unicos.append(encoding)
    return encodings_unicos


def normaliza_decimal(value):
    if value is None:
        return Decimal("0")

    if isinstance(value, Decimal):
        return value

    texto = str(value).strip().replace(" ", "")
    if not texto:
        return Decimal("0")

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    return Decimal(texto)


def normaliza_conteudo_ofx(ofx_file):
    conteudo = ofx_file.getvalue()

    for encoding in detecta_encodings_ofx(conteudo):
        try:
            texto = conteudo.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        texto = conteudo.decode("latin-1", errors="replace")

    def substitui_valor(match):
        tag, valor = match.groups()
        try:
            return f"{tag}{normaliza_decimal(valor)}"
        except InvalidOperation:
            return match.group(0)

    return AMOUNT_TAG_PATTERN.sub(substitui_valor, texto)


def carrega_ofx(ofx_file):
    conteudo_normalizado = normaliza_conteudo_ofx(ofx_file)
    return OfxParser.parse(StringIO(conteudo_normalizado))


def formata_valor(value):
    value = f"{normaliza_decimal(value):,.2f}"
    return "R$ " + value.replace(",", "X").replace(".", ",").replace("X", ".")


def normaliza_historico(memo):
    if memo is None:
        return "(Sem histórico)"
    memo = str(memo).strip()
    return memo if memo else "(Sem histórico)"


def historicos_selecionados(historicos, key_prefix):
    if st.button("Selecionar todos", key=f"selecionar_todos_{key_prefix}", use_container_width=True):
        for historico in historicos:
            st.session_state[f"{key_prefix}_{historico}"] = True

    selecionados = []
    for historico in historicos:
        checkbox_key = f"{key_prefix}_{historico}"
        if st.checkbox(historico, key=checkbox_key):
            selecionados.append(historico)
    return selecionados


st.title("Leitor de OFX")
ofx_file = st.file_uploader("Anexe o OFX", type=["ofx"], accept_multiple_files=False)
if ofx_file is not None:
    ofx = carrega_ofx(ofx_file)

    account = ofx.account
    statement = account.statement
    lista_transacoes = []
    for transaction in statement.transactions:
        valor = normaliza_decimal(transaction.amount)
        lista_transacoes.append(
            [
                transaction.type,
                transaction.date,
                valor,
                normaliza_historico(transaction.memo),
            ]
        )

    df = pd.DataFrame(lista_transacoes, columns=["Tipo", "Data", "Valor", "Histórico"])
    df["Valor"] = df["Valor"].apply(normaliza_decimal)
    df_creditos = df[df["Tipo"] == "credit"]
    df_debitos = df[df["Tipo"] == "debit"]

    historicos_credito = sorted(df_creditos["Histórico"].dropna().unique(), key=str.lower)
    historicos_debito = sorted(df_debitos["Histórico"].dropna().unique(), key=str.lower)

    col_tabela, col_painel = st.columns([1.8, 1.2], gap="large")

    with col_tabela:
        df_exibicao = df.copy()
        df_exibicao["Data"] = pd.to_datetime(df_exibicao["Data"]).dt.strftime("%d/%m/%Y %H:%M")
        df_exibicao["Valor"] = df_exibicao["Valor"].apply(formata_valor)
        st.dataframe(df_exibicao, use_container_width=True, height=620)

    with col_painel:
        filtros_credito, filtros_debito = st.columns(2, gap="medium")

        with filtros_credito:
            st.subheader("Históricos de Entradas")
            selecionados_credito = historicos_selecionados(historicos_credito, "credito")

        with filtros_debito:
            st.subheader("Históricos de Saídas")
            selecionados_debito = historicos_selecionados(historicos_debito, "debito")

        total_creditos = (
            sum(
                df_creditos[df_creditos["Histórico"].isin(selecionados_credito)]["Valor"],
                Decimal("0"),
            )
            if selecionados_credito
            else sum(df_creditos["Valor"], Decimal("0"))
        )
        total_debitos = (
            sum(
                df_debitos[df_debitos["Histórico"].isin(selecionados_debito)]["Valor"],
                Decimal("0"),
            )
            if selecionados_debito
            else sum(df_debitos["Valor"], Decimal("0"))
        )

        metrica_entrada, metrica_saida = st.columns(2)
        with metrica_entrada:
            st.metric("Total de Entradas", formata_valor(total_creditos))
        with metrica_saida:
            st.metric("Total de Saídas", formata_valor(total_debitos))
