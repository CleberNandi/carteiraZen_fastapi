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
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxrender1 libgl1 libgl1-mesa-glx ffmpeg libgtk-3-0 libv4l-dev libjpeg-dev \
    libavcodec-dev libavformat-dev libswscale-dev libatlas-base-dev libpng-dev openssl bash curl && \
    rm -rf /var/lib/apt/lists/*

# Copia apenas os arquivos necessários do builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# wait-for-it
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

EXPOSE 8000

CMD ["/wait-for-it.sh", "db:5432", "--timeout=60", "--strict", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
