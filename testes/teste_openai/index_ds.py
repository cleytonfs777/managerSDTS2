from dotenv import load_dotenv
import os
import numpy as np
import pandas as pd
import google.generativeai as genai

load_dotenv()


def consulta_ai(prompt_ia):

    token_gemini = os.getenv("TOKEN_GEMINI")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

    response = model.generate_content(prompt_ia)

    return response.text


prompt_ia = f'Se eu te passar um endereço voce consegue me retornar uma coordenada?'


if __name__ == '__main__':
    print(consulta_ai(prompt_ia))