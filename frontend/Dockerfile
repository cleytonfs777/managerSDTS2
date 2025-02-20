# Usar imagem Node.js como base
FROM node:18

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Copiar apenas os arquivos essenciais para otimizar cache
COPY package.json package-lock.json ./

# Instalar dependências
RUN npm install

# Copiar o restante do código
COPY . .

# Compilar o frontend para produção
RUN npm run build

# Expor a porta correta para o Railway
EXPOSE 4173

# Iniciar o servidor Svelte no modo de preview, permitindo acesso externo
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]
