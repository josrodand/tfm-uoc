import streamlit as st
import requests

st.set_page_config(page_title="Chat RAG", page_icon="🤖", layout="centered")

# URL
API_URL = "http://localhost:8000/invoke"  

st.title("🧠 AID-BOT Chat")
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

    # Llamada a la API
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = requests.post(API_URL, json={"query": prompt})
                response.raise_for_status()  # Verifica si hubo errores en la solicitud
                response_data = response.json()
                bot_response = response_data.get("response", "No se recibió respuesta.")
            except requests.exceptions.RequestException as e:
                bot_response = f"❌ Error al conectar con la API: {e}"

            st.markdown(bot_response["response"])

    # Guardar respuesta del asistente
    st.session_state.messages.append({"role": "assistant", "content": bot_response})