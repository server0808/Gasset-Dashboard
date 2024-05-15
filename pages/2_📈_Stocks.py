import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
from scipy.stats import kurtosis, skew

st.title("Stocks")
st.write("""Digite o ticker de algum ativo de sua preferência listado na base de dados do Yahoo Finance.
        Escolha o período desejado (data de início e data final). Um gráfico de preços será plotado abaixo.""")

ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Início')
end_date = st.sidebar.date_input('Fim')

# Conferindo link URL
if ticker is None or ticker == "":
    st.info("Por favor, digite o ticker para prosseguir.")

else:
    data = yf.download(tickers=ticker, start=start_date, end=end_date)
    fig = px.line(data_frame=data, x=data.index, y=data['Adj Close'], title=ticker + ' Price', color_discrete_sequence=["#B40404"])
    st.plotly_chart(fig)

    statistics_data, financial_data, news_data, gpt_stocks = st.tabs(['Statistics', 'Financial Data', 'News', 'ChatGPT with Stocks'])

    with statistics_data:
        # Returns
        st.subheader('Retornos')

        # Drop Some Columns
        data_stats = data.drop(columns=['Open','High', 'Low', 'Close', 'Volume'])

        # Create the 'Returns' column and drop NA values
        data_stats['Retornos (%)'] = (data['Adj Close']/data['Adj Close'].shift(1)-1)*100
        data_stats = data_stats.dropna()
    
        # Reset Index and Convert 'Date' Column
        data_stats = data_stats.reset_index()
        data_stats['Date'] = data_stats['Date'].dt.date
        data_stats = data_stats.set_index('Date')

        st.write(data_stats)

        st.subheader('Estatísticas Descritivas')    

        # Histogram of Returns
        fig = px.histogram(data_frame=data_stats, 
                       x='Retornos (%)', 
                       title='Histograma dos Retornos Diários', 
                       color_discrete_sequence=["#B40404"])
        st.plotly_chart(fig)

        # Distribution of Returns
        fig = ff.create_distplot(hist_data=[data_stats['Retornos (%)'].values.tolist()],
                             curve_type='kde',
                             group_labels=['Retornos (%)'],
                             show_hist=True)
        st.plotly_chart(fig)

        # Descriptive Statistics
        mean_returns = np.mean(data_stats['Retornos (%)'])
        std_returns = np.std(data_stats['Retornos (%)'])
        kurtosis_returns = kurtosis(data_stats['Retornos (%)'])
        skewness_returns = skew(data_stats['Retornos (%)'])

        # Puting into a pandas dataframe
        stats = {"Retorno Diário Médio": mean_returns, 
                "Volatilidade Diária": std_returns, 
                "Curtose": kurtosis_returns, 
                "Assimetria": skewness_returns}
        df_stats = pd.DataFrame(data=stats, index=[ticker])

        st.write(df_stats)