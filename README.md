# CarteiraZen

> Autor: Cleber Goulart Nandi

API robusta para gestão financeira, construída com FastAPI, focada em rastreabilidade, auditoria completa e automação de operações. Possui arquitetura profissional, seeds inteligentes (incluindo usuário system), testes automatizados, integração com Docker, múltiplos ambientes via Dynaconf, lint, formatação e deploy facilitado.

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

## Auditoria, Rastreabilidade e Usuário System

- Todas as operações de criação, atualização e deleção em recursos principais (ex: usuários, bancos) são auditadas automaticamente.
- Auditoria híbrida: cada registro possui campos de auditoria (`created_by`, `updated_by`, `deleted_by`, etc.) e todas as ações são registradas em uma tabela de auditoria dedicada.
- O usuário especial `system` é criado automaticamente via seed e utilizado para operações automatizadas e rastreáveis.
- O seed completo pode ser executado manualmente com:

```bash
python -m app.scripts.seed_all
```

## Consultando Auditoria

Exemplo de consulta de auditoria para ações em usuários:

```bash
curl -X GET "http://localhost:8000/api/v1/auditoria/?tabela=users"
curl -X GET "http://localhost:8000/api/v1/auditoria/?tabela=users&acao=update"
```

## Testes Automatizados

- O projeto possui testes automatizados para todos os fluxos de usuários, bancos e auditoria.
- Para rodar os testes:

```bash
make test
```

## Observações Adicionais

- O fluxo de seeds garante rastreabilidade desde o início do banco, sempre utilizando o usuário system para operações automáticas.
- Para expandir auditoria para novos módulos, siga o padrão já implementado em `users` e `bancos`.

---

> Projeto inicializado com ❤️ e FastAPI. Evoluído com foco em rastreabilidade e auditoria.
