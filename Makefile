# ========================
# Makefile para projeto CarteiraZen (refatorado)
# ========================

# ========================
# Variáveis gerais
# ========================
PROJECT_NAME=carteirazen
UV=uv
APP_DIR=app
TEST_DIR=tests
PORT ?= 8000
ENV_MODE ?= dev

# ========================
# Variáveis do banco
# ========================
DB_NAME ?= carteirazen_db
DB_USER ?= postgres
DB_PASS ?= postgres
DB_HOST ?= localhost
DB_PORT ?= 5432

# ========================
# Docker images
# ========================
DOCKER_BASE_IMAGE=clebernandi/fastapi-base:latest
DOCKER_APP_IMAGE=clebernandi/carteirazen-app:latest

# ========================
# Comandos principais
# ========================

.PHONY: install sync install-pre-commit precommit

install:
	$(UV) pip install -e .[dev]

sync:
	uv sync

install-pre-commit:
	pre-commit install

precommit:
	pre-commit run --all-files

# ========================
# Rodar FastAPI
# ========================
.PHONY: run dev hml

run:
	ENV_MODE=prod uv run uvicorn $(APP_DIR).main:app --host 0.0.0.0 --port $(PORT)

dev:
	ENV_MODE=dev uv run uvicorn $(APP_DIR).main:app --host 0.0.0.0 --port $(PORT) --reload

hml:
	ENV_MODE=hml uv run uvicorn $(APP_DIR).main:app --host 0.0.0.0 --port $(PORT) --reload

# Ngrok
.PHONY: ngrok dev-ngrok

ngrok:
	ENV_MODE=dev ngrok http $(PORT)

dev-ngrok:
	@echo "🚀 Rodando FastAPI com uv e ngrok..."
	@ENV_MODE=dev uv run uvicorn $(APP_DIR).main:app --host 0.0.0.0 --port $(PORT) --reload & \
	sleep 2 && \
	ngrok http $(PORT)

# ========================
# Testes
# ========================
.PHONY: test coverage

test:
	ENV_MODE=test pytest
coverage:
	ENV_MODE=test pytest --cov=$(APP_DIR) --cov-report=term-missing --cov-report=html --cov-report=xml

# ========================
# Linter e formatação
# ========================
.PHONY: lint fix format typecheck

lint:
	ruff check $(APP_DIR) $(TEST_DIR)

fix:
	ruff check $(APP_DIR) $(TEST_DIR) --fix

format:
	ruff format $(APP_DIR) $(TEST_DIR)

typecheck:
	pyright

# ========================
# Docker
# ========================
.PHONY: docker-base-build docker-base-push docker-app-build docker-app-push

docker-base-build:
	docker build -f Docker.base -t $(DOCKER_BASE_IMAGE) .

docker-base-push:
	docker push $(DOCKER_BASE_IMAGE)

docker-app-build:
	docker build -t $(DOCKER_APP_IMAGE) .

docker-app-push:
	docker push $(DOCKER_APP_IMAGE)

# Docker Compose
.PHONY: docker-up-build docker-up-build-db docker-up docker-up-db

docker-up-build-db:
	docker compose up --build db

docker-up-build:
	docker compose up --build

docker-up-db:
	docker compose up db

docker-up:
	docker compose up

# ========================
# Limpeza
# ========================
.PHONY: clean clean-docker clean-docker-all

clean:
	find . -type d -name "__pycache__" -exec rm -r {} + || true
	find . -type f -name "*.pyc" -delete || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache

clean-docker:
	docker compose down --rmi all --remove-orphans
	docker system prune -af

clean-docker-all:
	docker compose down -v --rmi all --remove-orphans
	docker system prune -af

# ========================
# Backup / restore DB
# ========================
.PHONY: backup-db restore-db

backup-db:
	docker exec db pg_dump -U $$POSTGRES_USER $$POSTGRES_DB > backup.sql

restore-db:
	cat backup.sql | docker exec -i db psql -U $$POSTGRES_USER $$POSTGRES_DB

# ========================
# Alembic migrations
# ========================
.PHONY: makemigrations migrate

makemigrations:
	@echo "📝 Criando migration automática para $(ENV_MODE)"
	ENV_MODE=$(ENV_MODE) alembic revision --autogenerate -m "Auto migration"

migrate:
	@echo "🚀 Aplicando migrations em $(ENV_MODE)"
	ENV_MODE=$(ENV_MODE) alembic upgrade head

# ========================
# Reset DB local
# ========================
.PHONY: reset-db-local reset-db

reset-db-local:
	@echo "🎯 Dropando banco $(DB_NAME)..."
	PGPASSWORD=$(DB_PASS) dropdb --if-exists --host=$(DB_HOST) --port=$(DB_PORT) --username=$(DB_USER) $(DB_NAME)
	@echo "✅ Banco removido."
	@echo "🎯 Criando banco $(DB_NAME)..."
	PGPASSWORD=$(DB_PASS) createdb --host=$(DB_HOST) --port=$(DB_PORT) --username=$(DB_USER) $(DB_NAME)
	@echo "✅ Banco criado."
	@echo "🎯 Executando migrations..."
	ENV_MODE=dev alembic upgrade head
	@echo "✅ Reset completo!"

reset-db:
	docker exec -it db psql -U postgres -c "DROP DATABASE IF EXISTS $(DB_NAME);"
	docker exec -it db psql -U postgres -c "CREATE DATABASE $(DB_NAME);"
	ENV_MODE=dev alembic upgrade head

# ========================
# Git helpers
# ========================
.PHONY: commit push

commit:
	@git commit -m "$(msg)"

push:
	@git push

# ========================
# Ajuda
# ========================
.PHONY: help

help:
	@echo "Comandos disponíveis:"
	@echo "  make install          Instala dependências com uv"
	@echo "  make sync             Sincroniza dependências"
	@echo "  make install-pre-commit  Instala hooks pre-commit"
	@echo "  make precommit        Executa pre-commit"
	@echo "  make run              Sobe FastAPI (prod)"
	@echo "  make dev              Sobe FastAPI (dev, reload)"
	@echo "  make hml              Sobe FastAPI (hml, reload)"
	@echo "  make ngrok            Expõe FastAPI via ngrok"
	@echo "  make dev-ngrok        Dev + ngrok"
	@echo "  make test             Executa testes com pytest"
	@echo "  make coverage         Testes com cobertura"
	@echo "  make lint             Verifica estilo com Ruff"
	@echo "  make fix              Corrige código automaticamente com Ruff"
	@echo "  make format           Formata código com Ruff"
	@echo "  make typecheck        Checa tipos com Pyright"
	@echo "  make docker-base-build  Build imagem base"
	@echo "  make docker-base-push   Push imagem base"
	@echo "  make docker-app-build   Build imagem do app"
	@echo "  make docker-app-push    Push imagem do app"
	@echo "  make docker-up-build-db  Sobe DB com build"
	@echo "  make docker-up-build     Sobe todos serviços com build"
	@echo "  make docker-up-db         Sobe DB"
	@echo "  make docker-up            Sobe todos serviços"
	@echo "  make clean            Limpa caches e pyc"
	@echo "  make clean-docker     Limpa containers e imagens (mantém volumes)"
	@echo "  make clean-docker-all Limpa tudo incluindo volumes"
	@echo "  make backup-db        Backup do DB"
	@echo "  make restore-db       Restore do DB"
	@echo "  make makemigrations  Cria migration automática (ENV_MODE)"
	@echo "  make migrate         Aplica migrations (ENV_MODE)"
	@echo "  make reset-db-local   Reseta DB local"
	@echo "  make reset-db         Reseta DB via container"
