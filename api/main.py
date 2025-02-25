from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from fastapi.middleware.cors import CORSMiddleware
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from time import sleep
import os
# Modulo criados
from crawlers import atribuir_documento
from utils import tranform_text_atribuicao
from google_sheets import main

# Carregar variáveis de ambiente
load_dotenv()


app = FastAPI()

# Configuração do CORS para permitir comunicação com o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Em produção, substitua pelo domínio correto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}


# Criar o endpoint FastAPI que usa StreamingResponse
@app.post("/atribuicao")
def atribuir(numSei: str, etiqueta: str, msg: str, atribuicao: str, assunto: str, status: str, categoria: str, grava_reg_sei: str):
    return StreamingResponse(
        atribuir_documento(numSei, etiqueta, msg, atribuicao, assunto, status, categoria, grava_reg_sei),
        media_type="text/plain"
    )



@app.get("/criar-oficio")
def criar_oficio(numSei: str, criacao: str, assunto: str, tipdoc: str, reference: str, detinatarios: str, considerandos: str, complementar: str, pronome: str, assinador: str):
    # Criar os paragrafos criando a api da 
    ...


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
