import streamlit as st

st.set_page_config(page_title="Gasset Dashboard")
st.title("Gasset Dashboard")
st.subheader("Nós apresentamos a nossa dashboard que compila dados de ações e dados macroeconômicos.")
st.write("""Deseja-se buscar dados de ações, criando histogramas de retornos e outras estatísticas descritivas, 
         dados macroeconômicos como inflação, curva de juros, preços de commodities etc.""")
st.caption("Criador: Davi Andrade")

st.subheader("Informações Importantes")
st.write("Os dados aqui apresentados possuem uma série de fontes, que estão elencadas a seguir. Os códigos são de autoria própria.")

st.link_button(url="https://platform.openai.com/docs/overview")
st.link_button(url="https://finance.yahoo.com")
st.link_button(url="https://www3.bcb.gov.br/sgspub")
st.link_button(url="https://www.ibge.gov.br/")
