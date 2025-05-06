# streamlit_app.py

import streamlit as st
# from src.rag_app.chain import RAGChain
from src.rag_app.graph import MultiAgentGraph

st.set_page_config(page_title="Chat RAG", page_icon="🤖", layout="centered")

# Inicializar el RAGChain
@st.cache_resource
def load_rag_chain():
    return MultiAgentGraph()

rag_chain = load_rag_chain()

st.title("🧠 Chat con RAGChain")
st.markdown("Asistente conversacional de ayudas a empresas.")

# Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada del usuario
prompt = st.chat_input("Escribe tu pregunta aquí...")

if prompt:
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Llamada a RAGChain
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = rag_chain.invoke(prompt)
            except Exception as e:
                response = f"❌ Error: {e}"

            st.markdown(response)

    # Guardar respuesta del asistente
    st.session_state.messages.append({"role": "assistant", "content": response})
