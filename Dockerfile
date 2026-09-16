# Etapa de build
FROM clebernandi/fastapi-base:latest AS builder

WORKDIR /app

# Apenas os arquivos de dependências para aproveitar cache
COPY pyproject.toml settings.toml README.md ./

# Copia o código fonte
COPY app ./app

# Instala dependências do projeto
RUN pip install --upgrade pip setuptools wheel && \
    pip install .

# Etapa final
FROM python:3.13-slim AS final

WORKDIR /app

# Libs necessárias em tempo de execução
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    libffi-dev \
    libssl-dev \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas os arquivos necessários do builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# wait-for-it
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh


# Script de inicialização
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000

ENTRYPOINT ["/app/start.sh"]
