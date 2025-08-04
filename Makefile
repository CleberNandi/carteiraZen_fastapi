# Makefile para projeto CarteiraZen com uv, ruff, pytest, pyright, etc.

# ========================
# Variáveis
# ========================
PROJECT_NAME=carteirazen
UV=uv
APP_DIR=app
TEST_DIR=tests

# ========================
### Variáveis do banco
# ========================
DB_NAME ?= carteirazen_db
DB_USER ?= postgres
DB_PASS ?= postgres
DB_HOST ?= localhost
DB_PORT ?= 5432

# ========================
### Docker image names
# ========================
DOCKER_BASE_IMAGE=clebernandi/fastapi-base:latest
DOCKER_APP_IMAGE=clebernandi/carteirazen-app:latest

# ========================
# Comandos principais
# ========================

# Instalação
.PHONY: install
# Instala dependências usando uv
install:
	$(UV) pip install -e .[dev]

# Atualizar dependências conforme pyproject.toml
.PHONY: sync
sync:
	uv sync

# Instala as dependências do projeto e hooks do pre-commit
install-pre-commit:
	pre-commit install

# Pre-commit (se configurado)
.PHONY: precommit
precommit:
	pre-commit run --all-files

# Inicia o servidor FastAPI em modo desenvolvimento com recarregamento automático
run:
	ENV_MODE=prod uv run uvicorn app.main:app --host 0.0.0.0 --port 8000  --reload

# Inicia o servidor FastAPI em modo desenvolvimento, recarregando ao alterar arquivos em app/
dev:
	ENV_MODE=dev uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


hml:
	ENV_MODE=hml uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: dev ngrok
# Rodar ngrok para expor porta 8000
ngrok:
	ENV_MODE=dev ngrok http 8000

# Executa os testes automatizados com pytest, garantindo que o diretório app seja encontrado
# pelo Python (PYTHONPATH=.)
.PHONY: test
test:
	ENV_MODE=test pytest

 # Testes com cobertura (opcional)
.PHONY: coverage
coverage:
	ENV_MODE=test pytest --cov=$(APP_DIR) --cov-report=term-missing

# Executa o linter Ruff para verificar problemas de estilo e código em app e tests
.PHONY: lint
lint:
	ruff check $(APP_DIR) $(TEST_DIR)

# Fix automático com Ruff
.PHONY: fix
fix:
	ruff check $(APP_DIR) $(TEST_DIR) --fix

# Formata o código de app e tests usando Ruff
format:
	ruff format $(APP_DIR) $(TEST_DIR)

# Tipagem com Pyright
.PHONY: typecheck
typecheck:
	pyright

# Build da imagem base
.PHONY: docker-base-build
docker-base-build:
	docker build -f Docker.base -t $(DOCKER_BASE_IMAGE) .

# Push da imagem base para Docker Hub
.PHONY: docker-base-push
docker-base-push:
	docker push $(DOCKER_BASE_IMAGE)

# Build da imagem do app usando a imagem base
.PHONY: docker-app-build
docker-app-build:
	docker build -t $(DOCKER_APP_IMAGE) .

# Push da imagem do app para Docker Hub
.PHONY: docker-app-push
docker-app-push:
	docker push $(DOCKER_APP_IMAGE)

# Up com build no docker-compose
.PHONY: docker-up-build-db
docker-up-build-db:
	docker compose up --build db

.PHONY: docker-up-build
docker-up-build:
	docker compose up --build

# Up sem build, usa imagens locais ou do hub
.PHONY: docker-up-db
docker-up-db:
	docker compose up db

.PHONY: docker-up
docker-up:
	docker compose up

# Remove todos os containers e imagens, mas mantém os volumes (dados do banco)
clean-docker:
	docker compose down --rmi all --remove-orphans
	docker system prune -af

# Remove tudo, inclusive volumes (dados do banco serão apagados!)
clean-docker-all:
	docker compose down -v --rmi all --remove-orphans
	docker system prune -af

# Backup do banco Postgres do container db para o arquivo backup.sql
backup-db:
	docker exec db pg_dump -U $$POSTGRES_USER $$POSTGRES_DB > backup.sql

# Restore do banco Postgres do arquivo backup.sql para o container db
restore-db:
	cat backup.sql | docker exec -i db psql -U $$POSTGRES_USER $$POSTGRES_DB

commit:
	@git commit -m "$(msg)"

push:
	@git push

# Alembic migrations
.PHONY: migrate
migrate:
	ENV_MODE=dev alembic upgrade head

.PHONY: makemigrations
makemigrations:
	ENV_MODE=dev alembic revision --autogenerate -m "Auto migration"

# Limpeza de arquivos pyc, cache etc
.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache

# Target para resetar o banco inteiro
.PHONY: reset-db-local
reset-db-local:
	@echo "🎯 Dropando banco $(DB_NAME)..."
	PGPASSWORD=$(DB_PASS) dropdb --if-exists --host=$(DB_HOST) --port=$(DB_PORT) --username=$(DB_USER) $(DB_NAME)
	@echo "✅ Banco removido."

	@echo "🎯 Criando banco $(DB_NAME)..."
	PGPASSWORD=$(DB_PASS) createdb --host=$(DB_HOST) --port=$(DB_PORT) --username=$(DB_USER) $(DB_NAME)
	@echo "✅ Banco criado."

	@echo "🎯 Executando migrations..."
	alembic upgrade head
	@echo "✅ Reset completo!"

.PHONY: reset-db
reset-db:
	docker exec -it db psql -U postgres -c "DROP DATABASE IF EXISTS carteirazen_db;"
	docker exec -it db psql -U postgres -c "CREATE DATABASE carteirazen_db;"
	alembic upgrade head

# ========================
# Ajuda
# ========================
.PHONY: help
help:
	@echo "Comandos disponíveis:"
	@echo "  make install         Instala com uv"
	@echo "  make sync            Sincroniza deps conforme pyproject.toml"
	@echo "  make test            Roda os testes"
	@echo "  make coverage        Testes com cobertura"
	@echo "  make lint            Valida com Ruff"
	@echo "  make fix             Corrige com Ruff"
	@echo "  make format          Formata com Ruff"
	@echo "  make typecheck       Verifica tipos com Pyright"
	@echo "  make run             Sobe o servidor FastAPI (modo dev)"
	@echo "  make makemigrations  Cria migração com Alembic"
	@echo "  make migrate         Aplica as migrações"
	@echo "  make precommit       Roda pre-commit em todos arquivos"
	@echo "  make clean           Limpa arquivos temporários"
