# CarteiraZen

> Autor: Cleber Goulart Nandi

Projeto base para aplicações FastAPI, com estrutura profissional, configuração por Dynaconf, suporte a Docker, testes, lint e deploy.

## Estrutura de Pastas

```
carteirazen/
├── app/
│   ├── api/
│   ├── config/
│   ├── core/
│   ├── crud/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── main.py
├── settings.toml
├── secret.toml (ou .secrets.toml)
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env
├── .gitignore
└── tests/
```

## Principais Comandos

- `make install` — Instala dependências do projeto
- `make run` — Sobe o servidor FastAPI em modo dev
- `make dev` — Sobe o servidor com recarregamento de arquivos
- `make run-prod` — Sobe o servidor em modo produção (Dynaconf prod)
- `make test` — Executa os testes
- `make lint` — Lint com Ruff
- `make format` — Formata o código
- `make up` — Sobe o ambiente Docker
- `make clean-docker` — Remove containers, imagens e volumes Docker

## Configuração

- Variáveis de ambiente e segredos: `settings.toml` e `secret.toml` (ou `.secrets.toml`)
- Para alternar ambientes Dynaconf, use a variável `ENV_FOR_DYNACONF` (ex: `ENV_FOR_DYNACONF=prod make run-prod` ou configure no `.env`)

## Debug no VS Code

- Use o launch.json já configurado para depurar com breakpoints.

## Docker

- O projeto já está pronto para build e deploy com Docker e docker-compose.
- O Dockerfile usa Alpine e instala dependências essenciais.

## Observações

- O projeto oculta automaticamente a documentação do FastAPI em produção.
- Estrutura pronta para crescer, com separação de camadas (api, core, crud, db, models, schemas).
- Use Dynaconf para múltiplos ambientes e segredos.

## Exemplos de uso dos endpoints User (CRUD)

### Criar usuário
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"name": "João", "email": "joao@email.com"}'
```

### Listar usuários
```bash
curl -X GET "http://localhost:8000/api/v1/users/"
```

### Buscar usuário por ID
```bash
curl -X GET "http://localhost:8000/api/v1/users/1"
```

### Buscar usuário por email
```bash
curl -X GET "http://localhost:8000/api/v1/users/email/joao@email.com"
```

### Atualizar usuário
```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
     -H "Content-Type: application/json" \
     -d '{"name": "João da Silva", "email": "joao@email.com"}'
```

### Deletar usuário
```bash
curl -X DELETE "http://localhost:8000/api/v1/users/1"
```

---

> Projeto inicializado com ❤️ e FastAPI.
