#!/bin/bash
set -e

# Espera o banco ficar pronto
echo "⏳ Aguardando o banco de dados em db:5432..."
/wait-for-it.sh db:5432 --timeout=60 --strict -- echo "✅ Banco de dados disponível!"

# Rodar migrações só em dev/hml
if [[ "$ENV_MODE" == "dev" || "$ENV_MODE" == "hml" ]]; then
    echo "🌱 Verificando migrations Alembic para $ENV_MODE..."

    CURRENT=$(ENV_MODE=$ENV_MODE alembic current --verbose | grep 'Current revision' | awk '{print $3}')
    HEAD=$(ENV_MODE=$ENV_MODE alembic heads | awk '{print $1}')

    if [[ "$CURRENT" == "$HEAD" ]]; then
        echo "✅ Banco já atualizado (revision: $CURRENT)"
    else
        echo "🚀 Executando migrations..."
        ENV_MODE=$ENV_MODE alembic upgrade head
        echo "✅ Migrations aplicadas. Nova versão:"
        ENV_MODE=$ENV_MODE alembic current
    fi
else
    echo "⚡ Ambiente $ENV_MODE detectado, pulando migrations."
fi

# Iniciar a API
echo "🚀 Iniciando Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
