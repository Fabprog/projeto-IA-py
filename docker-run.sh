#!/bin/bash

# Script para executar o projeto com Docker

echo "🐳 Iniciando Assistente Financeiro com Docker..."

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📝 Copie .env.docker para .env e configure sua GROQ_API_KEY"
    echo "cp .env.docker .env"
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.dev.yml down

# Construir e iniciar
echo "🔨 Construindo e iniciando containers..."
docker-compose -f docker-compose.dev.yml up --build -d

# Aguardar MySQL inicializar
echo "⏳ Aguardando MySQL inicializar..."
sleep 10

# Mostrar logs
echo "📋 Logs da aplicação:"
docker-compose -f docker-compose.dev.yml logs -f app