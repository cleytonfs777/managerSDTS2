<script>
    import { page } from '$app/state';
    import "bootstrap/dist/css/bootstrap.min.css";
</script>

<style>
    /* Estilos gerais */
    .container-flex {
        display: flex;
        height: 100vh;
    }

    /* Menu lateral */
    .sidebar {
        background: #081d33;
        width: 260px;
        color: white;
        display: flex;
        flex-direction: column;
        padding: 20px;
        transition: width 0.3s;
        min-height: 100vh;
    }

    .sidebar h3 {
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        color: #ff9900;
    }

    /* Links do menu */
    .nav-link {
        color: white;
        display: flex;
        align-items: center;
        padding: 12px;
        border-radius: 5px;
        font-size: 18px;
        transition: background 0.3s;
        text-decoration: none;
        margin-bottom: 10px;
    }

    .nav-link:hover {
        background: #ff9900;
    }

    /* Página ativa */
    .active {
        background: #ff4500 !important;
    }

    /* Ícones */
    .nav-icon {
        margin-right: 10px;
        font-size: 20px;
    }

    /* Conteúdo principal */
    .content {
        flex-grow: 1;
        padding: 20px;
        background: #f8f9fa;
    }
</style>

<div class="container-flex">
    <!-- MENU LATERAL -->
    <nav class="sidebar">
        <h3>📌 SDTS - Sistema</h3>

        <a href="/atribuicao" class="nav-link {page.url.pathname === '/atribuicao' ? 'active' : ''}">
            <span class="nav-icon">📄</span> Atribuição
        </a>
        
        <a href="/diarias" class="nav-link {page.url.pathname === '/diarias' ? 'active' : ''}">
            <span class="nav-icon">📅</span> Diárias
        </a>

        <a href="/fornecimento" class="nav-link {page.url.pathname === '/fornecimento' ? 'active' : ''}">
            <span class="nav-icon">📦</span> Fornecimento
        </a>
    </nav>

    <!-- CONTEÚDO PRINCIPAL -->
    <div class="content">
        <slot /> <!-- Renderiza a página atual -->
    </div>
</div>
