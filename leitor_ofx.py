from ofxparse import OfxParser
import streamlit as st
import pandas as pd

def formata_valor(value):
    value = f'{value:,.2f}'
    return "R$ " + value.replace(",","X").replace(".",",").replace("X",".")

st.title("Leitor de OFX -- Entradas")
ofx_file = st.file_uploader("Anexe o OFX",".ofx",False)
if ofx_file is not None:
    ofx = OfxParser.parse(ofx_file)    

    account = ofx.account
    statement = account.statement
    total_creditos = 0
    total_debitos = 0
    lista_transacoes = []
    for transaction in statement.transactions:
        if transaction.type == "credit":
            total_creditos += transaction.amount
        elif transaction.type == "debit":
            total_debitos += transaction.amount    
        lista_transacoes.append([transaction.type,
                                    transaction.date,
                                    formata_valor(transaction.amount),
                                    transaction.memo])       
    df = pd.DataFrame(lista_transacoes,columns=["Tipo","Data","Valor","Histórico"])       
    st.dataframe(df)
    col1,col2=st.columns(2)
    with col1:
        st.metric("Total de Entradas",formata_valor(total_creditos))
    with col2:
        st.metric("Total de Saídas",formata_valor(total_debitos))                       