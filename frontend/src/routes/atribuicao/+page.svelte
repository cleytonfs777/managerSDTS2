<script>
  import { onMount } from "svelte";
  import { listaAllNames, status, categoria, etiqueta } from "$lib/loadData";
  import { generateText } from "$lib/generateText";
  import { API_URL } from "$lib/config";

  let numSei = "";
  let assunto = "";
  let complemento = "";
  let atribuicao = "";
  let gravaSei = "";
  let statusSelecionado = "";
  let categoriaSelecionada = "";
  let etiquetaSelecionada = "";

  
  /** @type {string[]} */
  let atribuicoes = [];
  let gravaSeiOptions = ["Sim", "Não"];
  /**
   * @type {any[]}
   */
  let statusOptions = [];
  // @ts-ignore
  /**
   * @type {any[]}
   */
  let categoriaOptions = [];
  // @ts-ignore
  /**
   * @type {any[]}
   */
  let etiquetaOptions = [];

  onMount(async () => {
    atribuicoes = await listaAllNames();
    statusOptions = status();
    categoriaOptions = categoria();
    etiquetaOptions = etiqueta();

    // Definir valores padrão para os selects
    atribuicao = "Maj Giovanny"; // ✅ Atribuição padrão
    statusSelecionado = "Concluído"; // ✅ Status padrão
    categoriaSelecionada = "Rádio"; // ✅ Categoria padrão
    etiquetaSelecionada = "Aguardando Despacho do Major"; // ✅ Etiqueta padrão
    gravaSei = "Sim"; // ✅ Gravação SEI padrão
  });

  let artigoSelecionado = "o";
  let nomeOficio = "";
  /** @type {string[]} */
  let documentos = [];

  let textoGerado = "";
  let contadorCaracteres = 0;
  let ultrapassouLimite = false;
  let processandoEnvio = false;
  /** @type {string[]} */
  let respostaAPI = [];
  let progresso = 0;

  function adicionarDocumento() {
    if (nomeOficio.trim() !== "") {
      documentos = [...documentos, `${artigoSelecionado} ${nomeOficio}`];
      nomeOficio = "";
    }
  }

  // @ts-ignore
  function removerDocumento(index) {
    documentos = documentos.filter((_, i) => i !== index);
  }

  async function gerarTextoFinal() {
    if (!atribuicao || !assunto || documentos.length === 0) {
      alert("Preencha todos os campos antes de gerar o texto!");
      return;
    }

    textoGerado = await generateText(atribuicao, assunto, documentos, complemento);
    contadorCaracteres = textoGerado.length;
    ultrapassouLimite = contadorCaracteres > 250;
  }


  // @ts-ignore
  async function enviarDadosParaAPI() {
    if (!numSei || !etiquetaSelecionada || !assunto || !textoGerado) {
        alert("Preencha todos os campos e gere o texto antes de enviar!");
        return;
    }

    processandoEnvio = true;
    respostaAPI = ["Enviando requisição para a API..."];
    progresso = 0;

    try {
        // Construir a URL com os parâmetros como query string
        const url = new URL(API_URL);
        url.search = new URLSearchParams({
            numSei: numSei.trim(),
            etiqueta: etiquetaSelecionada.trim(),
            msg: textoGerado.trim(),
            atribuicao: atribuicao.trim(),
            assunto: assunto.trim(),
            status: statusSelecionado.trim(),
            categoria: categoriaSelecionada.trim(),
            grava_reg_sei: gravaSei.trim(),
        }).toString();

        const response = await fetch(url, {
            method: "POST",
            mode: "cors",
            headers: { "Content-Type": "application/json" }
        });

        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${await response.text()}`);
        }

        respostaAPI = [];

        // Ler a resposta em tempo real
        // @ts-ignore
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            let text = decoder.decode(value, { stream: true });

            respostaAPI = [...respostaAPI, text];

            // Atualiza progresso baseado nas etapas recebidas
            progresso = Math.min(respostaAPI.length * 10, 100);
        }
    } catch (error) {
        // @ts-ignore
        respostaAPI = [`Erro: ${error.message}`];
    } finally {
        processandoEnvio = false;
    }
}


</script>


<h1 class="text-center text-primary">💣 Atribuição de SEI</h1>

<div class="form-container">
  <form>
    <div class="row">
      <div class="col-md-6">
        <label for="num_sei" class="form-label">Número SEI:</label>
        <input
          type="text"
          id="num_sei"
          bind:value={numSei}
          class="form-control"
        />
      </div>
      <div class="col-md-6">
        <label for="assunto" class="form-label">Assunto:</label>
        <input
          type="text"
          id="assunto"
          bind:value={assunto}
          class="form-control"
        />
      </div>
    </div>

    <div class="row mt-3">
      <div class="col-md-6">
        <label for="complemento" class="form-label">Complemento:</label>
        <input
          type="text"
          id="complemento"
          bind:value={complemento}
          class="form-control"
        />
      </div>
      <div class="col-md-6">
        <label for="atribuicao" class="form-label">Atribuição:</label>
        <select id="atribuicao" class="form-select" bind:value={atribuicao}>
          <option value="">Selecione</option>
          {#each atribuicoes as item}
            <option>{item}</option>
          {/each}
        </select>
      </div>
    </div>

    <div class="row mt-3">
      <div class="col-md-6">
        <label for="grava_sei" class="form-label">Grava SEI:</label>
        <select id="grava_sei" class="form-select" bind:value={gravaSei}>
          <option value="">Selecione</option>
          {#each gravaSeiOptions as item}
            <option>{item}</option>
          {/each}
        </select>
      </div>
      <div class="col-md-6">
        <label for="status" class="form-label">Status:</label>
        <select id="status" class="form-select" bind:value={statusSelecionado}>
          <option value="">Selecione</option>
          {#each statusOptions as item}
            <option>{item}</option>
          {/each}
        </select>
      </div>
    </div>

    <div class="row mt-3">
      <div class="col-md-6">
        <label for="categoria" class="form-label">Categoria:</label>
        <select
          id="categoria"
          class="form-select"
          bind:value={categoriaSelecionada}
        >
          <option value="">Selecione</option>
          {#each categoriaOptions as item}
            <option>{item}</option>
          {/each}
        </select>
      </div>
      <div class="col-md-6">
        <label for="etiqueta" class="form-label">Etiqueta:</label>
        <select
          id="etiqueta"
          class="form-select"
          bind:value={etiquetaSelecionada}
        >
          <option value="">Selecione</option>
          {#each etiquetaOptions as item}
            <option>{item}</option>
          {/each}
        </select>
      </div>
    </div>
    <hr class="my-4">
    <!-- Formulário Processamento -->
    <div class="container mt-3">
      <div class="row">
        <!-- Select "o" ou "a" -->
        <div class="col-md-2">
          <select class="form-select" bind:value={artigoSelecionado}>
            <option value="o">o</option>
            <option value="a">a</option>
          </select>
        </div>

        <!-- Input de Nome -->
        <div class="col-md-4">
          <input
            type="text"
            class="form-control"
            placeholder="Nome do Ofício"
            bind:value={nomeOficio}
          />
        </div>

        <!-- Botão de Adicionar -->
        <div class="col-md-3">
          <button class="btn-add" on:click={adicionarDocumento}>➕</button>
        </div>
      </div>

      <!-- Lista de Documentos Adicionados -->
      {#if documentos.length > 0}

        <div class="documentos-container">
          {#each documentos as doc, index}
            <div class="d-flex justify-content-between align-items-center">
              <span>➡ {doc}</span>
              <button
                class="btn-delete"
                on:click={() => removerDocumento(index)}>🗑️</button
              >
            </div>
          {/each}
        </div>
      {/if}
    </div>
    <hr class="my-4">

    <!-- Botão Gerar Texto -->
    <button class="btn btn-dark mt-3" on:click={gerarTextoFinal}>Gerar Texto</button>

    <!-- Mensagem de alerta se ultrapassar 250 caracteres -->
    {#if textoGerado}
        <div class="mt-3">
            {#if ultrapassouLimite}
                <div class="alert alert-danger">⚠️ O texto gerado tem mais de 250 caracteres! ⚠️</div>
            {:else}
                <div class="alert alert-success">✅ O texto está dentro do limite permitido.</div>
            {/if}
        </div>

        <!-- Caixa de Texto Gerado -->
        <textarea class="form-control mt-2" rows="4" readonly bind:value={textoGerado}></textarea>
        <small class="text-muted d-block text-end">{contadorCaracteres}/250</small>
    {/if}

    <hr class="my-4">
    <!-- Botão de Envio -->
    <button type="button" class="btn-submit mt-4" on:click={enviarDadosParaAPI} disabled={processandoEnvio}>
      {processandoEnvio ? "Enviando..." : "Enviar"}
    </button>

    <!-- Barra de Progresso -->
    {#if processandoEnvio}
    <div class="progress mt-3">
      <div 
        class="progress-bar progress-bar-striped progress-bar-animated bg-info" 
        role="progressbar" 
        style="width: {progresso}%; transition: width 0.5s;">
        {progresso}%
      </div>
    </div>
  {/if}
  

    <!-- Exibir Resposta da API -->
    {#if respostaAPI.length > 0}
      <div class="alert alert-info mt-3">
        {#each respostaAPI as status}
          <p>{status}</p>
        {/each}
      </div>
    {/if}

  </form>
</div>

<style>
  .documentos-container {
    background-color: #081d33; /* Azul escuro */
    padding: 15px;
    border-radius: 10px;
    color: white;
    margin-top: 15px;
  }

  .btn-add {
    background-color: #0056b3;
    color: white;
    border: none;
    font-size: 20px;
    width: 100%;
    height: 40px;
    border-radius: 5px;
  }

  .btn-add:hover {
    background-color: #003f7f;
  }

  .btn-delete {
    background-color: transparent;
    border: none;
    color: #ccc;
    font-size: 18px;
    cursor: pointer;
  }

  .btn-delete:hover {
    color: #ff4500;
  }

  .form-container {
    max-width: 900px;
    margin: auto;
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }

  .form-label {
    font-weight: bold;
    color: #081d33;
  }

  .btn-submit {
    background: #ff4500;
    border: none;
    color: white;
    font-size: 18px;
    padding: 10px;
    width: 100%;
    border-radius: 5px;
    cursor: pointer;
    transition: 0.3s;
  }

  .btn-submit:hover {
    background: #ff9900;
  }
</style>
