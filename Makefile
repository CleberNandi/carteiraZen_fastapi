# Makefile para projeto FastAPI

.PHONY: run dev test lint format install up clean-docker

# Instala as dependências do projeto e hooks do pre-commit
install:
	pre-commit install

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
test:
	ENV_MODE=test PYTHONPATH=. pytest

# Executa o linter Ruff para verificar problemas de estilo e código em app e tests
lint:
	ruff check app tests

# Formata o código de app e tests usando Ruff
format:
	ruff format app tests

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
