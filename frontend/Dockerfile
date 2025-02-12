# Usar imagem Node.js como base
FROM node:18

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos de dependências antes para otimizar cache
COPY package.json package-lock.json ./
RUN npm install

# Copiar o restante do código do frontend
COPY . .

# Compilar o frontend para produção
RUN npm run build

# Iniciar o servidor Svelte em modo de preview (porta 5173)
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
