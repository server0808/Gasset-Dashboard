import streamlit as st
import sidrapy as sidra
import pandas as pd
from bcb import sgs, Expectativas, currency
import plotly.express as px

st.title('Macro')
st.write("""Escolha uma variável macroeconômica de sua preferência. Em sequência, gráficos e análises aparecerão na tela.
         """)

with st.sidebar:
    ipca_var = st.selectbox("Inflação (IPCA)",
                            ("IPCA12m", 
                             "IPCA12m-Categorias", 
                             "IPCA-BCB", 
                             "IPCA-Difusão", 
                             "IPCA-Núcleos", 
                             "IPCA-ExpMensais", 
                             "IPCA-Exp12m"))

with st.sidebar:
    selic_var = st.selectbox("Selic",
                            ("Selic", 
                             "Selic-Exp"))


st.subheader("Dados Correntes")

################ Inflação medida pelo IPCA ##################

# Importa dados do IPCA (índice cheio e grupos, a partir de janeiro/2020)
# Variação mensal, acumulada em 12 meses e peso mensal
dados_brutos_ipca = list(
    map(
        # função que será repetida (a repetição se deve ao fato de que a função 'get_table' do pacote 'sidra' não é vetorizada)
        lambda variavel: (
            sidra.get_table(
                table_code = "7060",        # tabela mais recente
                territorial_level = "1", 
                ibge_territorial_code = "1",
                variable = variavel,
                classifications = { # índice cheio e grupos
                    "315": "7169,7170,7445,7486,7558,7625,7660,7712,7766,7786"
                    },
                period = "all"
                )
            ),
            
        # códigos da variável dentro da tabela (pro argumento variavel)
        ["63", "2265", "66"]
        )
    )

# Tratamento de dados do IPCA
dados_ipca = (
    pd.concat(dados_brutos_ipca) # concatenando os dataframes em uma única tabela
    .rename(columns = dados_brutos_ipca[0].iloc[0])
    .rename(
        columns = {
            "Mês (Código)": "data",
            "Valor": "valor",
            "Variável": "variavel",
            "Geral, grupo, subgrupo, item e subitem": "grupo"
            }
        )
    .query("valor not in ['Valor', '...']") # removendo a string 'valor' e '...', sendo estes o método de identificação de valores não disponíveis no database do SIDRA 
    .filter(items = ["data", "variavel", "grupo", "valor"], axis = "columns") # selecionando apenas a data, a var., o grupo e o seu respectivo valor
    .replace(
        to_replace = {
            "variavel": {
                "IPCA - Variação mensal": "Variação % mensal",
                "IPCA - Variação acumulada em 12 meses": "Variação acum. 12 meses",
                "IPCA - Peso mensal": "Peso mensal"
                },
            "grupo": {"\d.": ""}  # \d identifica um dígito na linguagem python
            },
        regex = True   # uso da regex para identificar expressões regulares (neste caso, "1.", "2,", ...)
        )
    .assign(      # uso do assign para tratamento dos dados de datas e floats  
        data = lambda x: pd.to_datetime(x.data, format = "%Y%m"),  # conversão para formato internacional (e.g. 2020-01-01)
        valor = lambda x: x.valor.astype(float)
    )
)

# Contribuição dos grupos para o IPCA mensal (variação * peso / 100, já que está multiplicado por 100)
dados_contribuicao = (
    dados_ipca
    .query(
        "variavel in ['Variação % mensal', 'Peso mensal']" # "and grupo not in 'Educação'"  # pego a variação e o peso mensais e removo o índice geral (headline), dado que quero analisar a contribuição idiossincrática dos grupo
        )
    .pivot(index = ["data", "grupo"], columns = "variavel", values = "valor")  # pivoto as variáveis em duas colunas distintas, separando-as e colocando seus respectivos valores (para isso, defino data e grupo como índices do dataframe)
    .assign(
        contribuicao = lambda x: x["Variação % mensal"] * x["Peso mensal"] / 100
        )["contribuicao"] # extraio do resultado da operação apenas a coluna contribuição (que foi criada acima através da operação algébrica) para facilitar o plot
    .unstack() # função utilizada para transformação dos dados
)


# Dados do IPCA Headline mensal
dados_ipca_head = (
    dados_ipca
    .query(
        "variavel in 'Variação % mensal' and grupo in 'Índice geral'"  # pego a variação e o peso mensais e o índice geral (headline)
        )
    .pivot(index = ["data", "grupo"], columns = "variavel", values = "valor")  # pivoto as variáveis em duas colunas distintas, separando-as e colocando seus respectivos valores (para isso, defino data e grupo como índices do dataframe)
    .unstack() # função utilizada para transformação dos dados
)


# Importa dados das classificações do IPCA (BCB, % a.m.)
dados_brutos_classificações = sgs.get(
    codes = {
        "Livres": 11428,
        "Alimentação no domicílio": 27864,
        "Serviços": 10844, 
        "Industriais": 27863,
        "Monitorados": 4449, 
        "Comercializáveis": 4447,
        "Não comercializáveis": 4448
        },
    start = "2022-01-01"
)


# Importa dados do índice de difusão no SGS/BCB
dados_brutos_difusao = sgs.get(codes = {"Índice de Difusão": 21379}, start = "2022-01-01")

# Importa dados dos 7 núcleos de inflação
dados_brutos_nucleos = sgs.get(
    codes = {
        "IPCA-EX0": 11427,
        "IPCA-EX1": 16121,
        "IPCA-EX2": 27838,
        "IPCA-EX3": 27839,
        "IPCA-MA": 11426,
        "IPCA-MS": 4466,
        "IPCA-DP": 16122,
        "IPCA-EXFE": 28751
        },
    start = "2022-01-01"
)


# Expectativas do IPCA
# Mensais
em = Expectativas()
ep_ipca_m = em.get_endpoint("ExpectativaMercadoMensais")
df_ipca_m_exp = (ep_ipca_m.query()
            .filter(ep_ipca_m.Indicador == 'IPCA')
            .filter(ep_ipca_m.Data >= "2022-10-01")
            .filter(ep_ipca_m.baseCalculo == '1')
            .filter(ep_ipca_m.DataReferencia == '12/2024')
            .select(ep_ipca_m.Data, ep_ipca_m.Media, ep_ipca_m.Mediana)
            .orderby(ep_ipca_m.Data.asc())
            .collect())
df_ipca_m_exp['Data'] = pd.to_datetime(df_ipca_m_exp['Data'], format='%Y/%m/%d', errors='coerce')


# Anuais
ep_ipca_a = em.get_endpoint("ExpectativasMercadoAnuais")
df_ipca_a_exp = (ep_ipca_a.query()
            .filter(ep_ipca_a.Indicador == 'IPCA')
            .filter(ep_ipca_a.Data >= "2022-10-01")
            .filter(ep_ipca_a.baseCalculo == '1')
            .filter(ep_ipca_a.DataReferencia == '2024')
            .select(ep_ipca_a.Data, ep_ipca_a.Media, ep_ipca_a.Mediana)
            .orderby(ep_ipca_a.Data.asc())
            .collect())
df_ipca_a_exp['Data'] = pd.to_datetime(df_ipca_a_exp['Data'], format='%Y/%m/%d', errors='coerce')


################ Selic ##################
# Meta Selic
selic = sgs.get({'Selic':432}, start = '2010-01-01')

# Expectativas Selic
em = Expectativas()
ep_selic = em.get_endpoint("ExpectativasMercadoSelic")
df_selic_exp = (ep_selic.query()
                .filter(ep_selic.Data >= '2022-10-01')
                .filter(ep_selic.baseCalculo == '1')
                .filter(ep_selic.Reuniao == 'R8/2024')
                .collect())
df_selic_exp['Data'] = pd.to_datetime(df_selic_exp['Data'], format='%Y/%m/%d', errors='coerce')



# Configs IPCA
if ipca_var is None or ipca_var == "":
    st.info("Escolha a variável macroeconômica para prosseguir.")
elif ipca_var == "IPCA12m":
    fig = px.line(data_frame=dados_ipca_head, title='IPCA Headline')
    st.plotly_chart(fig)
elif ipca_var == "IPCA12m-Categorias":
    fig = px.line(data_frame=dados_contribuicao, title='IPCA por Grupo Contribuinte')         
    st.plotly_chart(fig)
elif ipca_var == "IPCA-BCB":
    fig = px.line(data_frame=dados_brutos_classificações, title='IPCA por Classificação do BCB')
    st.plotly_chart(fig)
elif ipca_var == "IPCA-Difusão":
    fig = px.line(data_frame=dados_brutos_difusao, title='Índice de Difusão do IPCA\n\n % de Subitens com Variação Positiva')
    st.plotly_chart(fig)
elif ipca_var == "IPCA-Núcleos":
    fig = px.line(data_frame=dados_brutos_nucleos, title='IPCA por Núcleos')
    st.plotly_chart(fig)
elif ipca_var == "IPCA-ExpMensais":
    fig = px.line(data_frame=df_ipca_m_exp, x=df_ipca_m_exp['Data'], y=df_ipca_m_exp['Media'], title='Expectativas IPCA Mensal')
    st.plotly_chart(fig)
elif ipca_var == "IPCA-Exp12m":
    fig = px.line(data_frame=df_ipca_a_exp, x=df_ipca_a_exp['Data'], y=df_ipca_a_exp['Media'], title='Expectativas IPCA Anual')
    st.plotly_chart(fig)

# Configs Selic
if selic_var is None or selic_var == "":
    st.info("Escolha a variável macroeconômica para prosseguir.")
elif selic_var == "Selic":
    fig = px.line(data_frame=selic, title="Meta Selic")
elif selic_var == "Selic-Exp":
    fig = px.line(data_frame=df_selic_exp, x=df_selic_exp['Data'], y=df_selic_exp['Media'], title='Expectativas da Selic 12m.')
    st.plotly_chart(fig)