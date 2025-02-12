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

# FUNÇÕE DA ABA ATRAIBUIÇÕES
def iniciar_navegador():
    """Configura e retorna um navegador Selenium headless"""
    options = Options()
    options.add_argument("--headless")
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
def gerar_dsp(numSei="1400.01.0041101/2024-28", documento="Despacho", documentoResp="Ofício", descricao="Descentralização de credito para execução de DSP Técnica", resposta="Resposta a solicitação de Descentralização de crédito para DSP", ofref="Ofício 1006 (90857411)", destino="1400029 - 5º COB", val="R$ 300,00", justif="Realização de manutenção de computadores, instalação de roteador de internet e manutenção do sistema de som da SOU da 2ª Cia/9º BBM Lavras", etiqueta="Aguardando Despacho do Major", atribuicao="67869998672 - Giovanny Cesar De Abreu", msg="Encaminho a vossa senhoria documentação que trata de descentralização de crédito. Resp, Cap Cleyton"):

    # Carregar variáveis de ambiente
    SEIGOL = os.getenv("SEI_GOL")

    # Define variáveis globaiso
    adicionarBotao = True
    
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
        # SEGUNDA PARTE ################# #divArvoreAcoes > a:nth-child(1)

        # Insira no campo perquisa de id=txtPesquisaRapida o valor que está na variavel numSei
        navegador.find_element(
            By.ID, "txtPesquisaRapida").send_keys(SEIGOL, Keys.ENTER)

        # Aguarde até que o primeiro frame esteja presente e mude para ele
        wait = WebDriverWait(navegador, 10)

        # Aguarde até que o segundo frame esteja presente e mude para ele
        frame_2 = wait.until(EC.presence_of_element_located(
            (By.ID, 'ifrVisualizacao')))
        navegador.switch_to.frame(frame_2)

        navegador.find_element(
            By.XPATH, '//*[@id="divArvoreAcoes"]/a[1]').click()

        yield "Criando despacho de solicitação para a Gol!\n"

        # Insere o conteudo de msg no campo de mensagens //*[@id="txtFiltro"]
        navegador.find_element(
            By.XPATH, '//*[@id="txtFiltro"]').send_keys(documento)

        navegador.find_element(
            By.XPATH, '//*[@id="txtFiltro"]').send_keys(Keys.TAB, Keys.TAB, Keys.ENTER)

        navegador.find_element(
            By.XPATH, '//*[@id="txtDescricao"]').send_keys(descricao)

        navegador.find_element(
            By.CSS_SELECTOR, '#divOptPublico > div > label').click()

        navegador.find_element(
            By.XPATH, '//*[@id="btnSalvar"]').click()

        ############# ETAPA DE NOVA JANELA ##########################
        yield "Abrindo despacho para a edição...\n"
        # Salve o identificador da janela original
        original_window = navegador.current_window_handle

        print(f"Janela original: {original_window}")

        print(f"Janelas abertas: {navegador.window_handles}")

        # Obtenha o identificador da nova janela
        new_window = [
            window for window in navegador.window_handles if window != original_window][0]

        print(f"Janela nova: {new_window}")

        # Mude para a nova janela
        navegador.switch_to.window(new_window)

        # INJETA O CONTEUDO DO SEGUNDO FRAME
        navegador.switch_to.frame(3)

        # Substitua pelo seletor correto da sua div
        div_element = navegador.find_element(By.CSS_SELECTOR, "body")

        # Substitua o conteúdo do <p> por um <h3>
        novo_conteudo = bodyTexto1(ofref, destino, val, justif)

        navegador.execute_script(
            "arguments[0].innerHTML = arguments[1];", div_element, novo_conteudo)

        sleep(1)
        
        yield "Documento criado corretamente!\n"

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
        
        yield "Documento pronto para atribuição!\n"

        sleep(3)

        # Feche a nova janela
        navegador.close()

        # Mude de volta para a janela original
        navegador.switch_to.window(original_window)

        # Atualiza a pagina para aparecer o botão de atribuição
        navegador.refresh()

        # Atribuição para o Major

        # Aguarde até que o segundo frame esteja presente e mude para ele
        frame_2 = wait.until(EC.presence_of_element_located(
            (By.ID, 'ifrVisualizacao')))
        navegador.switch_to.frame(frame_2)

        navegador.find_element(
            By.XPATH, '//*[@id="divArvoreAcoes"]/a[22]').click()

        if adicionarBotao:
            navegador.find_element(
                By.CSS_SELECTOR, '#btnAdicionar').click()

        navegador.find_element(
            By.CSS_SELECTOR, '#selMarcador > div > span').click()

        # Aguardar que as opções estejam visíveis
        opcoes = WebDriverWait(navegador, 10).until(
            EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, "a.dd-option"))
        )

        # Iterar sobre as opções e clicar naquela que corresponde ao texto alvo
        for opcao in opcoes:
            texto = opcao.text.strip()
            if texto == etiqueta:
                opcao.click()
                break

        # Insere o conteudo de msg no campo de mensagens //*[@id="txaTexto"]
        navegador.find_element(By.XPATH, '//*[@id="txaTexto"]').send_keys(msg)

        # Clica atraves do XPATH no botão //*[@id="sbmSalvar"]
        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()
        yield "Despacho atribuído com sucesso!\n"


        print("Despacho realizado com sucesso. Aguardando atribuição...")

        # Atualiza a pagina
        navegador.refresh()

        navegador.switch_to.frame(1)

        # Faz um click no botao XPATH //*[@id="divArvoreAcoes"]/a[8]
        navegador.find_element(
            By.XPATH, '//*[@id="divArvoreAcoes"]/a[8]').click()

        # Script JavaScript para selecionar a opção pelo texto
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
        # Executar o script
        navegador.execute_script(script)

        # Clica no botao de XPATH //*[@id="sbmSalvar"]
        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()
        yield f"Atribuição ao {atribuicao} realizada!\n"

        sleep(1)

        print(
            "Atribuição realizada com sucesso. Aguardando registro em controle sei...")

        # INDO PARA O DOCUMENTO DE RESPONSTA

        # SEGUNDA PARTE ################# #divArvoreAcoes > a:nth-child(1)
        navegador.refresh()

        yield "Iniciando ofício de resposta a Unidade Solicitante!\n"

        # Insira no campo perquisa de id=txtPesquisaRapida o valor que está na variavel numSei
        navegador.find_element(
            By.ID, "txtPesquisaRapida").send_keys(numSei, Keys.ENTER)

        # Aguarde até que o primeiro frame esteja presente e mude para ele
        wait = WebDriverWait(navegador, 10)

        # Aguarde até que o segundo frame esteja presente e mude para ele
        frame_2 = wait.until(EC.presence_of_element_located(
            (By.ID, 'ifrVisualizacao')))
        navegador.switch_to.frame(frame_2)

        navegador.find_element(
            By.XPATH, '//*[@id="divArvoreAcoes"]/a[1]').click()

        # Insere o conteudo de msg no campo de mensagens //*[@id="txtFiltro"]
        navegador.find_element(
            By.XPATH, '//*[@id="txtFiltro"]').send_keys(documentoResp)

        navegador.find_element(
            By.XPATH, '//*[@id="txtFiltro"]').send_keys(Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.ENTER)

        navegador.find_element(
            By.XPATH, '//*[@id="txtDescricao"]').send_keys(resposta)

        navegador.find_element(
            By.CSS_SELECTOR, '#divOptPublico > div > label').click()

        navegador.find_element(
            By.XPATH, '//*[@id="btnSalvar"]').click()

        ############# ETAPA DE NOVA JANELA ##########################

        sleep(10)

        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()

        yield "Documento de resposta criado com sucesso!\n"

        # Atualiza a pagina
        navegador.refresh()

        navegador.switch_to.frame(1)

        # Faz um click no botao XPATH //*[@id="divArvoreAcoes"]/a[8]
        navegador.find_element(
            By.XPATH, '//*[@id="divArvoreAcoes"]/a[8]').click()


        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()


    except Exception as e:

        print(f"Erro: {e}")