import streamlit as st

st.set_page_config(page_title="Gasset Dashboard")
st.title("Gasset Dashboard")
st.subheader("Nós apresentamos a nossa dashboard que compila dados de ações e dados macroeconômicos.")
st.write("""Com ela é possível buscar dados de ações, criando histogramas de retornos e outras estatísticas descritivas, 
         dados macroeconômicos como inflação e juros no Brasil e conversar com nosso ChatBOT.""")
st.caption("Criador: Davi Andrade")

st.subheader("Informações Importantes")
st.write("Todas as fontes utilizadas na construção dessa página estão elencadas a seguir. Os códigos são de autoria própria e são encontrados no repositório abaixo.")
st.link_button(label="Repositório no Github", url="https://github.com/vitaldavi/Gasset-Dashboard")
st.link_button(label="OpenAI API", url="https://platform.openai.com/docs/overview")
st.link_button(label="Yahoo Finance", url="https://finance.yahoo.com")
st.link_button(label="Banco Central do Brasil", url="https://www3.bcb.gov.br/sgspub")
st.link_button(label="IBGE", url="https://www.ibge.gov.br/")
st.link_button(label="Streamlit", url="https://streamlit.io/")
