# 1️⃣ Entendimento do escopo

Você quer um app de gerenciamento financeiro pessoal com os seguintes conceitos:

* Contas: onde o dinheiro está (banco, cartão, carteira, etc.)
* Transações: registros de movimentações financeiras

  * Tipos: Despesa, Receita, Transferência
  * Despesa de Cartão: associada a uma fatura
* Faturas: para despesas de cartão, com data de fechamento, data de vencimento
* Categorias: para classificar transações (alimentação, transporte, salário, etc.)

Extras que podem entrar:

* Relatórios / Dashboard
* Alertas ou notificações de fatura / saldo baixo
* Sincronização entre dispositivos

# 2️⃣ Modelagem de Dados (PostgreSQL)

### Usuários

```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hashed VARCHAR(255),
    totp_secret VARCHAR(255),
    is_superuser BOOLEAN DEFAULT FALSE,
    is_2fa_enabled BOOLEAN DEFAULT FALSE,
    plan VARCHAR(20),
    created_at timestamp DEFAULT now() NOT NULL,
    updated_at timestamp NULL,
    deleted_at timestamp NULL,
    ativo bool NOT NULL
);
```

### Bancos (Global)

```sql
CREATE TABLE bancos (
    id serial4 PRIMARY KEY,
    nome varchar NOT NULL,
    codigo varchar NOT NULL,
    ispb varchar NULL,
    cnpj varchar NULL,
    site varchar NULL,
    created_at timestamp DEFAULT now() NOT NULL,
    updated_at timestamp NULL,
    deleted_at timestamp NULL,
    ativo bool NOT NULL,
    cor VARCHAR(7) NOT NULL
);
```

### Contas

```sql
CREATE TABLE contas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    saldo_cents BIGINT DEFAULT 0,
    cheque_especial_cents BIGINT DEFAULT 0,
    cor VARCHAR(7) NOT NULL,
    incluir_na_soma_inicial BOOLEAN NOT NULL DEFAULT TRUE,
    conta_padrao BOOLEAN NOT NULL DEFAULT FALSE,
    created_at timestamp DEFAULT now() NOT NULL,
    updated_at timestamp NULL,
    deleted_at timestamp NULL,
    ativo bool NOT NULL,
    usuario_id INT NOT NULL REFERENCES usuarios(id),
    banco_id INT NOT NULL REFERENCES bancos(id)
);
```

### Categorias

```sql
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    cor VARCHAR(7) NOT NULL,
    created_at timestamp DEFAULT now() NOT NULL,
    updated_at timestamp NULL,
    deleted_at timestamp NULL,
    ativo bool NOT NULL,
    usuario_id INT NOT NULL REFERENCES usuarios(id)
);
```

### SubCategorias

```sql
CREATE TABLE sub_categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    cor VARCHAR(7) NOT NULL,
    created_at timestamp DEFAULT now() NOT NULL,
    updated_at timestamp NULL,
    deleted_at timestamp NULL,
    ativo bool NOT NULL,
    categoria_id INT NOT NULL REFERENCES categorias(id),
    usuario_id INT NOT NULL REFERENCES usuarios(id)
);
```

### Cartões

```sql
CREATE TABLE cartoes (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(16) NOT NULL,
    descricao VARCHAR(20) NOT NULL,
    bandeira VARCHAR(20) NOT NULL,
    limite_cents BIGINT NOT NULL,
    fechamento DATE NOT NULL,
    vencimento DATE NOT NULL,
    cartao_padrao BOOLEAN NOT NULL DEFAULT FALSE,
    cor VARCHAR(7) NOT NULL,
    created_at timestamp DEFAULT now() NOT NULL,
    updated_at timestamp NULL,
    deleted_at timestamp NULL,
    ativo bool NOT NULL,
    conta_id INT NOT NULL REFERENCES contas(id),
    usuario_id INT NOT NULL REFERENCES usuarios(id)
);
```

### Faturas

```sql
CREATE TABLE faturas (
    id SERIAL PRIMARY KEY,
    valor_cents BIGINT NOT NULL,
    pago BOOLEAN DEFAULT FALSE,
    cor VARCHAR(7) NOT NULL,
    fechamento DATE NOT NULL,
    vencimento DATE NOT NULL,
    created_at timestamp DEFAULT now() NOT NULL,
    updated_at timestamp NULL,
    deleted_at timestamp NULL,
    ativo bool NOT NULL,
    conta_cartao_id INT NOT NULL REFERENCES cartoes(id),
    usuario_id INT NOT NULL REFERENCES usuarios(id)
);
```

### Transações

```sql
CREATE TABLE transacoes (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    valor_cents BIGINT NOT NULL,
    data_vencimento DATE NOT NULL,
    data_lancamento DATE NOT NULL,
    data_efetivacao DATE NOT NULL,
    encargos_cents BIGINT,
    descontos_cents BIGINT,
    recorrente BOOLEAN DEFAULT FALSE,
    descricao TEXT,
    efetivada BOOLEAN DEFAULT True,
    cor VARCHAR(7) NOT NULL,
    created_at timestamp DEFAULT now() NOT NULL,
    updated_at timestamp NULL,
    deleted_at timestamp NULL,
    ativo bool NOT NULL,
    transacao_pai_id INT,
    conta_origem_id INT REFERENCES contas(id),
    conta_destino_id INT REFERENCES contas(id),
    categoria_id INT REFERENCES categorias(id),
    sub_categoria_id INT REFERENCES sub_categorias(id),
    fatura_id INT REFERENCES faturas(id),
    usuario_id INT NOT NULL REFERENCES usuarios(id)
);
```

### Transações Parcelas

```sql
CREATE TABLE transacoes_parcelas (
    id SERIAL PRIMARY KEY,
    quantidade INT,
    parcela_inicial INT,
    periodicidade VARCHAR(20) DEFAULT 'mensal',
    created_at timestamp DEFAULT now() NOT NULL,
    updated_at timestamp NULL,
    deleted_at timestamp NULL,
    ativo bool NOT NULL,
    transacao_id INT REFERENCES transacoes(id),
    usuario_id INT NOT NULL REFERENCES usuarios(id)
);
```

* Fluxo de uso:

  1. Criar a transação principal (transacoes)
  2. Criar registro em transacoes\_parcelas
  3. Gerar parcelas explícitas em transacoes com transacao\_pai\_id apontando para a transação principal

# 3️⃣ Backend (FastAPI + Postgres)

* Estrutura básica de FastAPI:

```
zenny/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ config.py          # Dynaconf
│  │  ├─ security.py        # Hash, JWT, TOTP
│  │  ├─ database.py        # SQLAlchemy engine & session
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ usuario.py
│  │  ├─ banco.py
│  │  ├─ conta.py
│  │  ├─ categoria.py
│  │  ├─ sub_categoria.py
│  │  ├─ cartao.py
│  │  ├─ fatura.py
│  │  ├─ transacao.py
│  │  └─ transacao_parcela.py
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  ├─ usuario.py
│  │  ├─ banco.py
│  │  ├─ conta.py
│  │  ├─ categoria.py
│  │  ├─ sub_categoria.py
│  │  ├─ cartao.py
│  │  ├─ fatura.py
│  │  └─ transacao.py
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ v1/
│  │  │  ├─ __init__.py
│  │  │  ├─ usuario.py
│  │  │  ├─ banco.py
│  │  │  ├─ conta.py
│  │  │  ├─ categoria.py
│  │  │  └─ transacao.py
│  └─ services/
│     ├─ __init__.py
│     ├─ usuario_service.py
│     └─ transacao_service.py
├─ migrations/               # Alembic
├─ docker-compose.yml
├─ Dockerfile
├─ nginx/
│  ├─ default.conf
└─ .env

```

* Endpoints essenciais:

```
| Recurso     | Método | Descrição                                          |
| ----------- | ------ | -------------------------------------------------- |
| /contas     | GET    | Lista contas                                       |
| /contas     | POST   | Cria conta                                         |
| /categorias | GET    | Lista categorias                                   |
| /transacoes | GET    | Lista transações (filtros: data, conta, categoria) |
| /transacoes | POST   | Cria transação                                     |
| /faturas    | GET    | Lista faturas do cartão                            |
| /faturas    | POST   | Cria fatura                                        |
```

* Regras de negócio:

  * Se a transação for despesa de cartão, vincula a fatura mais próxima de fechamento
  * Transferência entre contas deve criar duas transações: saída e entrada
  * Atualizar saldo da conta automaticamente ao criar ou excluir transação

# 4️⃣ Frontend (React + React Native + Expo Router SDK 53)

* Telas principais:

  * Dashboard: resumo de saldo, gráficos e próximas faturas
  * Transações: listar, criar, filtrar
  * Contas: listar, criar
  * Categorias: listar, criar
  * Faturas: listar, criar (opcional, normalmente calculadas automaticamente)

* Fluxo da transação:

  1. Seleciona tipo (despesa, receita, transferência)
  2. Seleciona conta origem (e destino se transferência)
  3. Seleciona categoria
  4. Insere valor e data
  5. Se cartão, escolhe fatura ou define automática
  6. Salvar → toast + atualizar saldo

* Componentes reutilizáveis:

  * GenericForm

    * Modal de seleção para conta/categoria/fatura
    * Input com máscara de moeda
    * DatePicker
    * Lista filtrável com search

# 5️⃣ Próximos passos que eu sugiro

1. Refatorar backend:

   * Garantir modelo de transação consistente
   * Criar regras de negócio: transferência, fatura, atualização de saldo
2. Refatorar frontend:

   * Ajustar GenericForm para suportar modal de conta, categoria e fatura
   * Máscara de valores e picker de data
3. Integração:

   * Criar hooks para fetch com autenticação
   * Atualizar saldo ao criar/editar/excluir transações
   * Atualizar dashboards em tempo real (ou via refresh)
4. Extras avançados (opcional):

   * Push notifications para faturas próximas
   * Gráficos de despesas por categoria
   * Export CSV ou PDF do extrato

# 6️⃣ Regras de negócio que impactam modelagem

1. Transferência entre contas

   * Criar duas transações:

     * Saída da conta origem
     * Entrada na conta destino
   * Ambas vinculadas à mesma operação (pode ser operacao\_transferencia\_id ou transacao\_pai\_id)

2. Despesa de cartão

   * Ao lançar transação do cartão:

     * Associar à fatura vigente do cartão
     * Somar automaticamente à fatura
   * Evitar inconsistências de data

3. Parcelas

   * Cada parcela é uma transação separada, ligada à transação pai
   * Permite marcar parcelas individuais como efetivadas, excluir ou editar

4. Recorrência

   * Se recorrente, gerar transações futuras automaticamente (mensalmente, por exemplo)

# Tabelas e relacionamentos

```python-repl
USUARIOS
---------
id PK
nome
email
password_hashed
...
ativo

BANCOS
------
id PK
nome
codigo
...

CONTAS
------
id PK
nome
tipo
saldo_cents
usuario_id FK -> USUARIOS.id
banco_id FK -> BANCOS.id
...

CATEGORIAS
----------
id PK
nome
tipo
usuario_id FK (opcional) -> USUARIOS.id
...

SUB_CATEGORIAS
---------------
id PK
nome
tipo
categoria_id FK -> CATEGORIAS.id
usuario_id FK (opcional) -> USUARIOS.id

CARTOES
-------
id PK
descricao
numero
bandeira
usuario_id FK -> USUARIOS.id
conta_id FK -> CONTAS.id
...

FATURAS
-------
id PK
conta_cartao_id FK -> CARTOES.id
valor_cents
pago
...

TRANSACOES
-----------
id PK
tipo
valor_cents
conta_origem_id FK -> CONTAS.id
conta_destino_id FK -> CONTAS.id
categoria_id FK -> CATEGORIAS.id
sub_categoria_id FK -> SUB_CATEGORIAS.id
fatura_id FK -> FATURAS.id
transacao_pai_id FK -> TRANSACOES.id
usuario_id FK -> USUARIOS.id
...

TRANSACOES_PARCELAS
-------------------
id PK
transacao_id FK -> TRANSACOES.id (transação pai)
quantidade
parcela_inicial
periodicidade
...
```

# Relacionamentos principais

1. USUARIOS → CONTAS / CARTOES / TRANSACOES

   * Um usuário tem várias contas, cartões e transações.
2. BANCOS → CONTAS

   * Um banco pode ter várias contas.
3. CATEGORIAS → SUB\_CATEGORIAS

   * Cada categoria pode ter várias subcategorias.
   * Usuário pode ter categorias próprias (opcional).
4. CARTOES → FATURAS

   * Um cartão possui várias faturas.
5. TRANSACOES → CONTAS / CARTOES / FATURAS / CATEGORIAS / SUB\_CATEGORIAS

   * Uma transação pode:

     * Debitar de uma conta (conta\_origem)
     * Creditar outra conta (conta\_destino, para transferências)
     * Pertencer a uma categoria / subcategoria
     * Estar vinculada a uma fatura (despesa de cartão)
     * Ser uma parcela (transacao\_pai\_id)
6. TRANSACOES\_PARCELAS → TRANSACOES

   * Define quantidade de parcelas e periodicidade da transação pai.
   * Cada parcela é gerada como transação explícita em TRANSACOES.

# Observações do ERD

* Parcelas: cada parcela é uma linha em TRANSACOES apontando para a transação pai (transacao\_pai\_id).
* Recorrência: gerenciada em TRANSACOES\_PARCELAS (ex.: mensal, semanal).
* Soft delete: todas as tabelas principais têm deleted\_at + ativo.
