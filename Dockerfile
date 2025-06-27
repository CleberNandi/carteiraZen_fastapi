# Dockerfile para FastAPI
FROM python:3.13.3-alpine3.22

WORKDIR /app

# Instala dependências de build e sistema necessárias para Alpine
RUN apk add --no-cache build-base gcc musl-dev libffi-dev openssl-dev bash

COPY pyproject.toml ./
COPY settings.toml ./
COPY .secrets.toml ./
COPY app ./app

RUN pip install --upgrade pip setuptools wheel && \
    pip install 'uvicorn[standard]' && \
    pip install .

# Baixa o script wait-for-it para garantir que o app só inicia após o banco estar pronto
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

EXPOSE 8000

CMD ["/wait-for-it.sh", "db:5432", "--timeout=60", "--strict", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
