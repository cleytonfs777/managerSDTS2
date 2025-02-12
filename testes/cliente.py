import requests

def fazer_requisicao():
    """Faz requisição para a API FastAPI e imprime mensagens de status em tempo real"""

    url = "http://localhost:8000/atribuicao"  # Ajuste conforme a URL do servidor
    params = {
        "numSei": "1400.01.0005892/2025-68",
        "etiqueta": "Aguardando Despacho do Major",
        "msg": "Sr. Maj Giovanny. Encaminho a V.Sa. para análise e despacho o Ofício 34 (106066300), que trata de pagamento de dsp para militares especialistas. Resp, Cap Cleyton.",
        "atribuicao": "Maj Giovanny",
        "assunto": "Instalação de Repetidoras para funcionamento da rede rádio",
        "status": "Concluído",
        "categoria": "Rádio",
        "grava_reg_sei": "Sim"
    }

    print("Enviando requisição para a API...\n")

    try:
        response = requests.post(url, params=params, stream=True)
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    print(line.decode("utf-8"))
        else:
            print(f"Erro {response.status_code}: {response.text}")

    except requests.RequestException as e:
        print(f"Erro na requisição: {e}")

# Executar a função
if __name__ == "__main__":
    fazer_requisicao()
