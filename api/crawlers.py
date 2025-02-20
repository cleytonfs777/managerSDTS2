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
from time import sleep
import os
from textbase import bodyTexto1, bodyAssunto1
from utils import tranform_text_atribuicao
from google_sheets import main
from dotenv import load_dotenv

load_dotenv()

# FUNÇÕE DA ABA ATRAIBUIÇÕES
def iniciar_navegador():
    """Configura e retorna um navegador Selenium headless"""
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=service, options=options)
    navegador.implicitly_wait(10)
    return navegador

# Função geradora para enviar status em tempo real
def atribuir_documento(numSei, etiqueta, msg, atribuicao, assunto, status, categoria, grava_reg_sei):
    """Automação do SEI MG com status via StreamingResponse"""


    yield "Iniciando a automação...\n"
    
    navegador = iniciar_navegador()
    url = "https://www.sei.mg.gov.br"
    navegador.get(url)

    # Credenciais (deveriam vir de variáveis de ambiente)
    USER_ACCOUNT = os.getenv("SEI_USER", "08761724602")
    PASS_ACCOUNT = os.getenv("SEI_PASS")
    UNID_ACCOUNT = os.getenv("SEI_UNIDADE", "CBMMG")

    try:
        yield "Realizando login no SEI MG...\n"

        navegador.find_element(By.ID, "txtUsuario").send_keys(USER_ACCOUNT)
        navegador.find_element(By.ID, "pwdSenha").send_keys(PASS_ACCOUNT)

        # Selecionar o órgão no dropdown
        select_element = navegador.find_element(By.ID, "selOrgao")
        select = Select(select_element)
        select.select_by_visible_text(UNID_ACCOUNT)

        navegador.find_element(By.ID, "Acessar").click()
        yield "Login realizado com sucesso!\n"

        # Pesquisar documento
        navegador.find_element(By.ID, "txtPesquisaRapida").send_keys(numSei)
        navegador.find_element(By.ID, "txtPesquisaRapida").send_keys(Keys.ENTER)
        yield f"Pesquisando documento {numSei}...\n"

        # Aguardar e entrar no frame correto
        wait = WebDriverWait(navegador, 10)
        frame_2 = wait.until(EC.presence_of_element_located((By.ID, 'ifrVisualizacao')))
        navegador.switch_to.frame(frame_2)

        yield "Entrando na área de ações...\n"

        # Clicar no botão da árvore de ações
        botao = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#divArvoreAcoes > a:nth-child(22)")))
        botao.click()

        # Adicionar marcador
        navegador.find_element(By.CSS_SELECTOR, '#btnAdicionar').click()
        yield "Adicionando marcador...\n"

        seletor_l = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#selMarcador > div > a")))
        seletor_l.click()

        # Selecionar a etiqueta correta
        opcoes = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a.dd-option")))
        for opcao in opcoes:
            if opcao.text.strip() == etiqueta:
                opcao.click()
                break

        yield "Etiqueta selecionada!\n"

        # Inserir mensagem no campo de despacho
        navegador.find_element(By.XPATH, '//*[@id="txaTexto"]').send_keys(msg)
        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()
        yield "Despacho realizado com sucesso!\n"

        # Atualizar a página e atribuir documento
        navegador.refresh()
        navegador.switch_to.frame(1)

        element_8 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="divArvoreAcoes"]/a[8]')))
        element_8.click()

        # Converte texto de atribuição conforme json
        atribuicao = tranform_text_atribuicao(atribuicao)

        # Selecionar atribuição via JavaScript
        script = f"""
        var atribuicao = "{atribuicao}";
        var selectElement = document.querySelector("#selAtribuicao");
        for (var i = 0; i < selectElement.options.length; i++) {{
            if (selectElement.options[i].text === atribuicao) {{
                selectElement.selectedIndex = i;
                selectElement.dispatchEvent(new Event('change'));
                break;
            }}
        }}
        """
        navegador.execute_script(script)
        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()

        yield "Atribuição realizada com sucesso!\n"

        # Gravar no controle SEI (se necessário)
        if grava_reg_sei == "Sim":
            yield "Registrando no controle SEI...\n"
            
            # Chama a função para gravar no Google Sheets
            main([numSei, "", "", assunto, status, categoria, "Cap Cleyton"])
            
            yield "Registro em controle SEI realizado com sucesso!\n"
        else:
            yield "Registro em controle SEI não foi gravado.\n"

        yield "Processo concluído!\n"

    except Exception as e:
        yield f"Erro durante a execução: {e}\n"

    finally:
        navegador.quit()


# FUNÇÕE DA ABA DIÁRIAS
def gerar_dsp(numSei="1400.01.0041101/2024-28", documento="Despacho", documentoResp="Ofício",
              descricao="Descentralização de crédito para execução de DSP Técnica",
              resposta="Resposta a solicitação de Descentralização de crédito para DSP",
              ofref="Ofício 1006 (90857411)", destino="1400029 - 5º COB", val="R$ 300,00",
              justif="Realização de manutenção de computadores, instalação de roteador de internet e manutenção do sistema de som da SOU da 2ª Cia/9º BBM Lavras",
              etiqueta="Aguardando Despacho do Major", atribuicao="67869998672 - Giovanny Cesar De Abreu",
              msg="Encaminho a vossa senhoria documentação que trata de descentralização de crédito. Resp, Cap Cleyton"):

    SEIGOL = os.getenv("SEI_GOL", "1400.01.0007019/2025-97")
    yield "Iniciando a automação...\n"
    
    navegador = iniciar_navegador()
    url = "https://www.sei.mg.gov.br"
    navegador.get(url)

    # Credenciais (deveriam vir de variáveis de ambiente)
    USER_ACCOUNT = os.getenv("SEI_USER", "08761724602")
    PASS_ACCOUNT = os.getenv("SEI_PASS")
    UNID_ACCOUNT = os.getenv("SEI_UNIDADE", "CBMMG")

    try:
        yield "Realizando login no SEI MG...\n"

        # Aguarde até que o campo de usuário esteja visível antes de interagir
        wait = WebDriverWait(navegador, 10)  # Aguarde até 10 segundos
        usuario_input = wait.until(EC.presence_of_element_located((By.ID, "txtUsuario")))
        senha_input = wait.until(EC.presence_of_element_located((By.ID, "pwdSenha")))
        orgao_select = wait.until(EC.presence_of_element_located((By.ID, "selOrgao")))
        acessar_button = wait.until(EC.element_to_be_clickable((By.ID, "Acessar")))

        print(" Achou todos...")

        print(f"Usuário: {USER_ACCOUNT}")
        print(f"Senha: {PASS_ACCOUNT}")

        usuario_input.send_keys(USER_ACCOUNT)
        senha_input.send_keys(PASS_ACCOUNT)

        # Selecionar a unidade
        select = Select(orgao_select)
        select.select_by_visible_text(UNID_ACCOUNT)
        acessar_button.click()
        yield "Login realizado com sucesso!\n"

        # Aguardar e entrar no frame correto
        # wait = WebDriverWait(navegador, 10)
        # frame_2 = wait.until(EC.presence_of_element_located((By.ID, 'ifrVisualizacao')))
        # navegador.switch_to.frame(frame_2)

        # Pesquisar documento
        navegador.find_element(By.ID, "txtPesquisaRapida").send_keys(SEIGOL)
        navegador.find_element(By.ID, "txtPesquisaRapida").send_keys(Keys.ENTER)
        yield f"Pesquisando documento {SEIGOL}...\n"

        wait = WebDriverWait(navegador, 10)
        frame_2 = wait.until(EC.presence_of_element_located((By.ID, 'ifrVisualizacao')))
        navegador.switch_to.frame(frame_2)

        navegador.find_element(By.XPATH, '//*[@id="divArvoreAcoes"]/a[1]').click()
        yield "Criando despacho de solicitação para a Gol...\n"

        navegador.find_element(By.XPATH, '//*[@id="txtFiltro"]').send_keys(documento)
        navegador.find_element(By.XPATH, '//*[@id="txtFiltro"]').send_keys(Keys.TAB, Keys.TAB, Keys.ENTER)

        navegador.find_element(By.XPATH, '//*[@id="txtDescricao"]').send_keys(descricao)
        navegador.find_element(By.CSS_SELECTOR, '#divOptPublico > div > label').click()
        navegador.find_element(By.XPATH, '//*[@id="btnSalvar"]').click()

        yield "Abrindo despacho para edição...\n"

        sleep(1.5)

        # Mudança de janela para edição
        original_window = navegador.current_window_handle
        new_window = [window for window in navegador.window_handles if window != original_window][0]
        navegador.switch_to.window(new_window)

        navegador.switch_to.frame(3)
        div_element = navegador.find_element(By.CSS_SELECTOR, "body")

               # Substitua o conteúdo do <p> por um <h3>
        novo_conteudo = bodyTexto1(ofref, destino, val, justif)

        navegador.execute_script(
            "arguments[0].innerHTML = arguments[1];", div_element, novo_conteudo)

        sleep(1)

        navegador.switch_to.default_content()

        # LIMPA O CONTEUDO DO PRIMEIRO FRAME
        navegador.switch_to.frame(2)

        # Substitua pelo seletor correto da sua div
        div_element = navegador.find_element(By.CSS_SELECTOR, "body")

        div_element.send_keys("teste")

        novo_conteudo = bodyAssunto1(numSei)
        navegador.execute_script(
            "arguments[0].innerHTML = arguments[1];", div_element, novo_conteudo)

        navegador.switch_to.default_content()

        sleep(1)

        # Clica no botão de salvar
        div_element = navegador.find_element(
            By.CSS_SELECTOR, "#cke_149").click()

        sleep(3)

        yield "Documento salvo com sucesso!\n"

        # Feche a nova janela
        navegador.close()

        # Mude de volta para a janela original
        navegador.switch_to.window(original_window)

        # Atualiza a pagina para aparecer o botão de atribuição
        navegador.refresh()

        # Atribuição
        frame_2 = wait.until(EC.presence_of_element_located((By.ID, 'ifrVisualizacao')))
        navegador.switch_to.frame(frame_2)
        navegador.find_element(By.XPATH, '//*[@id="divArvoreAcoes"]/a[22]').click()
        navegador.find_element(By.CSS_SELECTOR, '#btnAdicionar').click()
        navegador.find_element(By.CSS_SELECTOR, '#selMarcador > div > span').click()

        opcoes = WebDriverWait(navegador, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a.dd-option"))
        )

        for opcao in opcoes:
            texto = opcao.text.strip()
            if texto == etiqueta:
                opcao.click()
                break

        navegador.find_element(By.XPATH, '//*[@id="txaTexto"]').send_keys(msg)
        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()
        yield "Despacho atribuído com sucesso!\n"

        navegador.refresh()
        navegador.switch_to.frame(1)

        navegador.find_element(By.XPATH, '//*[@id="divArvoreAcoes"]/a[8]').click()

        script = f"""
        var atribuicao = "{atribuicao}";
        var selectElement = document.querySelector("#selAtribuicao");
        for (var i = 0; i < selectElement.options.length; i++) {{
            if (selectElement.options[i].text === atribuicao) {{
                selectElement.selectedIndex = i;
                selectElement.dispatchEvent(new Event('change'));
                break;
            }}
        }}
        """
        navegador.execute_script(script)
        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()

        yield f"Atribuição ao {atribuicao} realizada!\n"

        navegador.refresh()
        yield "Iniciando ofício de resposta à Unidade Solicitante...\n"

        navegador.find_element(By.ID, "txtPesquisaRapida").send_keys(numSei, Keys.ENTER)
        frame_2 = wait.until(EC.presence_of_element_located((By.ID, 'ifrVisualizacao')))
        navegador.switch_to.frame(frame_2)

        navegador.find_element(By.XPATH, '//*[@id="divArvoreAcoes"]/a[1]').click()
        navegador.find_element(By.XPATH, '//*[@id="txtFiltro"]').send_keys(documentoResp)
        navegador.find_element(By.XPATH, '//*[@id="txtDescricao"]').send_keys(resposta)
        navegador.find_element(By.CSS_SELECTOR, '#divOptPublico > div > label').click()
        navegador.find_element(By.XPATH, '//*[@id="btnSalvar"]').click()

        sleep(10)
        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()
        yield "Documento de resposta criado com sucesso!\n"

    except Exception as e:
        yield f"Erro na execução: {e}"  # Agora a função sempre retorna um gerador


    finally:
        navegador.quit()

if __name__ == "__main__":
    print("Iniciando geração de DSP...")
    for mensagem in gerar_dsp():
        print(mensagem)
