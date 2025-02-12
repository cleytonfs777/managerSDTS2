import json
import os

caminho_completo = os.path.join(os.path.dirname(__file__), 'dadosmil.json')

print(f"O caminho completo é: {caminho_completo}")

def tranform_text_atribuicao(text):
    with open(caminho_completo) as json_file:
        dados = json.load(json_file)

        for chave, valor in dados.items():
            if valor[1] == text:
                return f"{chave} - {valor[0]}"
