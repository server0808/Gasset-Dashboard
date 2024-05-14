import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
from scipy.stats import kurtosis, skew
from yfclass import YahooFinanceToolSpec
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
import openai
from constant_openai import OPENAI_API_KEY


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

    with financial_data:
        
        # Balance Sheet
        st.subheader('Balance Sheet')
        yfinance_tool = YahooFinanceToolSpec()
        balance_sheet = yfinance_tool.balance_sheet(ticker)

        st.write(balance_sheet)

        # Income Statement
        st.subheader('Income Statement')
        income_stmt = yfinance_tool.income_statement(ticker)

        st.write(income_stmt)

        # Cash Flow
        st.subheader('Cash Flow')
        cash_flow = yfinance_tool.cash_flow(ticker)

        st.write(cash_flow)

        # Analyst Price Target
        #st.header('Analyst Price Target')
        #price_target = yfinance_tool.stock_analyst_target(ticker)

        #st.write(price_target)

        # Analysts Recommendations
        st.subheader('Analyst Recommendations')
        recommendations = yfinance_tool.stock_recommendations(ticker)

        st.write(recommendations)

        # Earnings
        st.subheader('Earnings')
        earnings = yfinance_tool.stock_earnings(ticker)

        st.write(earnings)

    with news_data:
        st.subheader('News')

    with gpt_stocks:
        st.subheader('Chat with GPTS Stocks')

        # LLM model
        llm = OpenAI(model='gpt-3.5-turbo', api_key=OPENAI_API_KEY)

        # Importing yfinance tools
        yfinance_tool = YahooFinanceToolSpec()
        yfinance_tool_list = yfinance_tool.to_tool_list()

        # Instantiating the OpenAI's agent
        agent = OpenAIAgent.from_tools(yfinance_tool_list, llm=llm)

        # Chatting with the agent
        input = f"What is the last price of {ticker} stock?"
        print(agent.chat("{input}"))