import streamlit as st
import requests
import time

# Definir a URL da API FastAPI
API_URL = "http://localhost:8000/status"

# Configuração da página do Streamlit
st.set_page_config(page_title="Monitoramento em Tempo Real", layout="centered")

# Título da aplicação
st.title("🔄 Monitoramento de Processo")

# Criar um botão para iniciar o processo
if st.button("Iniciar Processo"):
    status_container = st.empty()  # Criar um espaço dinâmico para atualizar status

    # Fazer a requisição à API FastAPI usando streaming
    response = requests.get(API_URL, stream=True)

    for line in response.iter_lines():
        if line:
            status_text = line.decode("utf-8")  # Decodificar a resposta da API
            status_container.write(f"✅ {status_text}")  # Exibir o status atualizado
            time.sleep(1)  # Pequena pausa para simular a atualização gradual
