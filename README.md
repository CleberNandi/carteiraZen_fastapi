# CarteiraZen

> Autor: Cleber Goulart Nandi

API robusta para gestão financeira, construída com FastAPI, focada em rastreabilidade, auditoria completa e automação de operações. Possui arquitetura profissional, seeds inteligentes (incluindo usuário system), testes automatizados, integração com Docker, múltiplos ambientes via Dynaconf, lint, formatação e deploy facilitado.

---

## Visão Geral do Projeto

CarteiraZen é uma API backend para gestão financeira pessoal e corporativa, com foco em segurança, rastreabilidade e auditoria detalhada.
Tecnologias principais: Python 3.10+, FastAPI, SQLAlchemy, Alembic, Docker, Dynaconf.

---

## Estrutura de Pastas

```
carteirazen/
├── app/
│   ├── api/
│   │   ├── agencias/
│   │   ├── auditoria/
│   │   ├── auth/
│   │   ├── bancos/
│   │   ├── cartoes/
│   │   ├── categorias/
│   │   ├── contas_correntes/
│   │   ├── faturas/
│   │   ├── transacoes/
│   │   └── users/
│   ├── config/
│   ├── core/
│   ├── crud/
│   │   ├── agencia.py
│   │   ├── auditoria.py
│   │   ├── banco.py
│   │   ├── cartao.py
│   │   ├── categoria.py
│   │   ├── conta_corrente.py
│   │   ├── fatura.py
│   │   ├── transacao.py
│   │   └── user.py
│   ├── db/
│   ├── models/
│   │   ├── agencia.py
│   │   ├── auditoria.py
│   │   ├── banco.py
│   │   ├── cartao.py
│   │   ├── categoria.py
│   │   ├── conta_corrente.py
│   │   ├── fatura.py
│   │   ├── mixins.py
│   │   ├── transacao.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── agencia.py
│   │   ├── auditoria.py
│   │   ├── banco.py
│   │   ├── cartao.py
│   │   ├── categoria.py
│   │   ├── conta_corrente.py
│   │   ├── fatura.py
│   │   ├── token.py
│   │   ├── transacao.py
│   │   └── user.py
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

---

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

---

## Configuração e Variáveis de Ambiente

- Variáveis de ambiente e segredos são configurados em `settings.toml` e `secret.toml` (ou `.secrets.toml`).
- Para alternar ambientes Dynaconf, use a variável `ENV_FOR_DYNACONF` (ex: `ENV_FOR_DYNACONF=prod make run-prod` ou configure no `.env`).
- Exemplo de variável importante:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/carteirazen
SECRET_KEY=uma_chave_secreta_para_tokens
```

---

## Como Rodar Localmente

1. Clone o repositório
2. Instale as dependências:

```bash
make install
```

3. Configure as variáveis de ambiente no arquivo `.env`
4. Rode as migrações do banco:

```bash
alembic upgrade head
```

5. Rode o servidor em modo desenvolvimento:

```bash
make run
```

6. Acesse a documentação interativa em: `http://localhost:8000/docs`

---

## Exemplos de Uso da API

### Consultar auditoria para usuários

```bash
curl -X GET "http://localhost:8000/api/v1/auditoria/?tabela=users"
```

### Criar um novo banco (exemplo)

```bash
curl -X POST "http://localhost:8000/api/v1/bancos/" \
-H "Content-Type: application/json" \
-d '{"nome": "Banco Exemplo", "codigo": "123"}'
```

---

## Debug no VS Code

- Use o `launch.json` já configurado para depurar com breakpoints.

---

## Docker

- O projeto já está pronto para build e deploy com Docker e docker-compose.
- O Dockerfile usa Alpine e instala dependências essenciais.
- Para subir o ambiente Docker:

```bash
make up
```

---

## Auditoria, Rastreabilidade e Usuário System

- Todas as operações de criação, atualização e deleção em recursos principais (ex: usuários, bancos) são auditadas automaticamente.
- Auditoria híbrida: cada registro possui campos de auditoria (`created_by`, `updated_by`, `deleted_by`, etc.) e todas as ações são registradas em uma tabela de auditoria dedicada.
- O usuário especial `system` é criado automaticamente via seed e utilizado para operações automatizadas e rastreáveis.
- O seed completo pode ser executado manualmente com:

```bash
python -m app.scripts.seed_all
```

---

## Testes Automatizados

- O projeto possui testes automatizados para todos os fluxos de usuários, bancos e auditoria.
- Para rodar os testes:

```bash
make test
```

---

## Observações Adicionais

- O fluxo de seeds garante rastreabilidade desde o início do banco, sempre utilizando o usuário system para operações automáticas.
- Para expandir auditoria para novos módulos, siga o padrão já implementado em `users` e `bancos`.

---

> Projeto inicializado com ❤️ e FastAPI. Evoluído com foco em rastreabilidade e auditoria.
