# Dockerfile para FastAPI
FROM python:3.12-alpine3.20

WORKDIR /app

# Instala dependências de build e sistema necessárias para Alpine
RUN apk add --no-cache build-base gcc musl-dev libffi-dev openssl-dev

COPY pyproject.toml ./
COPY settings.toml ./
COPY .secrets.toml ./
COPY app ./app

RUN pip install --upgrade pip setuptools wheel && \
    pip install 'uvicorn[standard]' && \
    pip install .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
