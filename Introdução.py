import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Gasset Dashboard")
st.title("Gasset Dashboard")
st.subheader("Nós apresentamos a nossa dashboard que compila dados de ações e dados macroeconômicos.")
st.write("""Deseja-se buscar dados de ações, criando histogramas de retornos e outras estatísticas descritivas, 
         dados macroeconômicos como inflação, curva de juros, preços de commodities etc.""")
st.caption("Criador: Davi Andrade")



st.subheader("Informações Importantes")
st.write("Os dados aqui apresentados possuem uma série de fontes, que estão elencadas a seguir. Os códigos são de autoria própria.")

