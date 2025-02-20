from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time

app = FastAPI()

async def gerar_status():
    """Função que envia mensagens de progresso antes da resposta final"""
    yield "Iniciando processo...\n"
    time.sleep(2)  # Simulando um processamento
    yield "Carregando dados...\n"
    time.sleep(2)
    yield "Processando informações...\n"
    time.sleep(5)
    yield "Finalizando...\n"
    time.sleep(2)
    yield "Processo concluído!\n"

@app.get("/status")
async def status_stream():
    return StreamingResponse(gerar_status(), media_type="text/plain")
