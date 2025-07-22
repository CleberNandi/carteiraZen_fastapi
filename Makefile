# Makefile para projeto CarteiraZen com uv, ruff, pytest, pyright, etc.

# ========================
# Variáveis
# ========================
PROJECT_NAME=carteirazen
UV=uv
APP_DIR=app
TEST_DIR=tests

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

# Sobe o docker-compose
up:
	docker-compose up

up-build:
	docker-compose up --build

# Remove todos os containers e imagens, mas mantém os volumes (dados do banco)
clean-docker:
	docker-compose down --rmi all --remove-orphans
	docker system prune -af

# Remove tudo, inclusive volumes (dados do banco serão apagados!)
clean-docker-all:
	docker-compose down -v --rmi all --remove-orphans
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
