import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage   
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
#import os
#from constant_openai import OPENAI_API_KEY

# Setting the API key
#os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Functions or Modules
def get_vectorstore_from_url(url):
    # Get the text in document format
    loader = WebBaseLoader(url)
    document = loader.load()

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(document)

    # Create a vectorstore from the chunks
    vector_store = Chroma.from_documents(document_chunks, OpenAIEmbeddings(api_key=openai_api_key))

    return vector_store

def get_context_retriever_chain(vector_store):

    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)

    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages([
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
      ("user", "Diante da conversa acima, gere uma pesquisa de busca para encontrar informações relevantes para a conversa.")
    ])

    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

    return retriever_chain

def get_conversational_rag_chain(retriever_chain):

    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)

    prompt = ChatPromptTemplate.from_messages([
      ("system", "Responda as perguntas do 'user' baseando-se no contexto providenciado a seguir:\n\n{context}"),
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}")
    ])

    stuff_documents_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def get_response(user_input):
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

    response = conversation_rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input": user_input
    })

    return response["answer"]

# Title and contextual info
st.title('Gasset ChatGPT')
st.write("Converse com nosso ChatBOT como desejar. Envie um link e faça perguntas acerca do conteúdo contido nele.")

# Sidebar
with st.sidebar:
    st.subheader("Configurações")
    link_url = st.text_input('Link (URL)')
    openai_api_key = st.text_input('OpenAI API Key', key='chatbot_api_key', type='password')
    st.write("[Obtenha uma chave de acesso](https://platform.openai.com/account/api-keys)")

# Conferindo chave de acesso OpenAI API
#if openai_api_key is None or openai_api_key == "":
    #st.info("Por favor, insira sua senha de acesso para prosseguir.")

# Conferindo link URL
if link_url is None or link_url == "" and openai_api_key is None or openai_api_key == "":
    st.info("Por favor, cole a URL e sua chave de acesso para prosseguir.")

else:
    # Session State
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Olá, eu sou o Gasset ChatBot. Como posso te ajudar?")
        ]

    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vectorstore_from_url(link_url)

    # User Input
    user_query = st.chat_input("Digite sua mensagem aqui...")
    if user_query is not None and user_query != "":
        response = get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))

    # Add Conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)

