import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
SPREADSHEET_ID = "1iGD_0kU_czJ365DzBNe6-n4lqkPE5eeByXgg9ZsaRgA"
RANGE_NAME = "2025!B:B"  # Apenas a coluna B (números SEI)


def get_credentials():
    """Obtém as credenciais do Google Sheets"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def verificar_sei_existente(service, sei_numero):
    """
    Verifica se o número SEI já está cadastrado na planilha (coluna B).
    Retorna True se já existir, False se não existir.
    """
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()

        valores = result.get('values', [])

        # Percorre todas as células da coluna B e verifica se o SEI já existe
        for linha in valores:
            if linha and linha[0] == sei_numero:
                return True  # SEI já cadastrado

        return False  # SEI não encontrado

    except HttpError as err:
        print(f"Erro ao verificar SEI: {err}")
        return False  # Assume que não existe para evitar bloqueio


def main(objetos: list = []):
    """Adiciona um novo registro ao Google Sheets se o SEI não existir"""

    creds = get_credentials()

    try:
        service = build("sheets", "v4", credentials=creds)

        sei_numero = objetos[0]  # Número SEI a verificar

        # Verifica se o SEI já existe antes de adicionar um novo registro
        if verificar_sei_existente(service, sei_numero):
            print("⚠️ SEI já cadastrado! Registro não será adicionado.")
            return "sei já cadastrado"

        # Obtém a última linha com dados para adicionar um novo registro
        SAMPLE_RANGE_NAME = "2025!A2:I"

        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SAMPLE_RANGE_NAME
        ).execute()

        values = result.get('values', [])
        next_row = len(values) + 1 if values else 1  # Próxima linha disponível

        # Dados para adicionar
        new_values = [[next_row] + objetos]  # Adiciona número da linha

        # Corpo da solicitação para append
        body = {'values': new_values}

        # Envia os dados para o Google Sheets
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SAMPLE_RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"✅ Valores adicionados com sucesso: {result.get('updates').get('updatedCells')}")
        return "registro adicionado"

    except HttpError as err:
        print(f"Erro ao adicionar registro: {err}")
        return "erro ao adicionar"


if __name__ == "__main__":
    # ["num_sei", "planilha", "frequencia", "descricao", "status", "categoria", "atendente"]
    lista_sei = ["1400.01.0026993/2024-25", "", "", "Concerto de repetidora portátil", "Concluído", "Telefonia", "Cap Cleyton"]
    resultado = main(lista_sei)
    print(f"Resultado: {resultado}")
