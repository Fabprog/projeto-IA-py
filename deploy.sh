#!/bin/bash

# Script de deploy para produção

echo "🚀 Iniciando deploy do Assistente Financeiro..."

# Verificar se arquivo de produção existe
if [ ! -f .env.production ]; then
    echo "❌ Arquivo .env.production não encontrado!"
    echo "📝 Copie .env.production.example para .env.production e configure"
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.prod.yml --env-file .env.production down

# Fazer backup do volume (opcional)
echo "💾 Fazendo backup do banco..."
docker run --rm -v projeto-ia-py_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Build e deploy
echo "🔨 Construindo e iniciando containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.production up --build -d

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 15

# Verificar status
echo "✅ Verificando status dos containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.production ps

echo "🎉 Deploy concluído!"
echo "📍 Aplicação disponível em: http://localhost:${APP_PORT:-5000}"