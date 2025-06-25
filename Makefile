# Makefile para projeto FastAPI

.PHONY: run dev test lint format install up clean-docker

# Instala as dependências do projeto e hooks do pre-commit
install:
	pre-commit install

# Inicia o servidor FastAPI em modo desenvolvimento com recarregamento automático
run:
	uv run uvicorn app.main:app --reload

# Inicia o servidor FastAPI em modo desenvolvimento, recarregando ao alterar arquivos em app/
dev:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-include app/*

# Executa os testes automatizados com pytest, garantindo que o diretório app seja encontrado
# pelo Python (PYTHONPATH=.)
test:
	PYTHONPATH=. pytest

# Executa o linter Ruff para verificar problemas de estilo e código em app e tests
lint:
	ruff check app tests

# Formata o código de app e tests usando Ruff
format:
	ruff format app tests

# Sobe o docker-compose
up:
	docker-compose up

# Remove todos os containers, imagens e volumes do projeto
clean-docker:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -af
