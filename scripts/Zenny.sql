CREATE TABLE "usuarios" (
  "id" SERIAL PRIMARY KEY,
  "nome" varchar(100),
  "email" varchar(100) UNIQUE,
  "password_hashed" varchar(255),
  "totp_secret" varchar(255),
  "is_superuser" boolean DEFAULT false,
  "is_2fa_enabled" boolean DEFAULT false,
  "plan" varchar(20),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp,
  "deleted_at" timestamp,
  "ativo" boolean
);

CREATE TABLE "bancos" (
  "id" serial PRIMARY KEY,
  "nome" varchar,
  "codigo" varchar,
  "ispb" varchar,
  "cnpj" varchar,
  "site" varchar,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp,
  "deleted_at" timestamp,
  "ativo" boolean,
  "cor" varchar(7)
);

CREATE TABLE "contas" (
  "id" serial PRIMARY KEY,
  "nome" varchar(100),
  "tipo" varchar(50),
  "saldo_cents" bigint DEFAULT 0,
  "cheque_especial_cents" bigint DEFAULT 0,
  "cor" varchar(7),
  "incluir_na_soma_inicial" boolean DEFAULT true,
  "conta_padrao" boolean DEFAULT false,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp,
  "deleted_at" timestamp,
  "ativo" boolean,
  "usuario_id" int,
  "banco_id" int
);

CREATE TABLE "categorias" (
  "id" serial PRIMARY KEY,
  "nome" varchar(100),
  "tipo" varchar(20),
  "cor" varchar(7),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp,
  "deleted_at" timestamp,
  "ativo" boolean,
  "usuario_id" int
);

CREATE TABLE "sub_categorias" (
  "id" serial PRIMARY KEY,
  "nome" varchar(100),
  "tipo" varchar(20),
  "cor" varchar(7),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp,
  "deleted_at" timestamp,
  "ativo" boolean,
  "categoria_id" int,
  "usuario_id" int
);

CREATE TABLE "cartoes" (
  "id" serial PRIMARY KEY,
  "numero" varchar(16),
  "descricao" varchar(20),
  "bandeira" varchar(20),
  "limite_cents" bigint,
  "fechamento" date,
  "vencimento" date,
  "cartao_padrao" boolean DEFAULT false,
  "cor" varchar(7),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp,
  "deleted_at" timestamp,
  "ativo" boolean,
  "conta_id" int,
  "usuario_id" int
);

CREATE TABLE "faturas" (
  "id" serial PRIMARY KEY,
  "valor_cents" bigint,
  "pago" boolean DEFAULT false,
  "cor" varchar(7),
  "fechamento" date,
  "vencimento" date,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp,
  "deleted_at" timestamp,
  "ativo" boolean,
  "conta_cartao_id" int,
  "usuario_id" int
);

CREATE TABLE "transacoes" (
  "id" serial PRIMARY KEY,
  "tipo" varchar(20),
  "valor_cents" bigint,
  "data_vencimento" date,
  "data_lancamento" date,
  "data_efetivacao" date,
  "encargos_cents" bigint,
  "descontos_cents" bigint,
  "recorrente" boolean DEFAULT false,
  "descricao" text,
  "efetivada" boolean DEFAULT true,
  "cor" varchar(7),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp,
  "deleted_at" timestamp,
  "ativo" boolean,
  "transacao_pai_id" int,
  "conta_origem_id" int,
  "conta_destino_id" int,
  "categoria_id" int,
  "sub_categoria_id" int,
  "fatura_id" int,
  "usuario_id" int
);

CREATE TABLE "transacoes_parcelas" (
  "id" serial PRIMARY KEY,
  "quantidade" int,
  "parcela_inicial" int,
  "periodicidade" varchar(20) DEFAULT 'mensal',
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp,
  "deleted_at" timestamp,
  "ativo" boolean,
  "transacao_id" int,
  "usuario_id" int
);

ALTER TABLE "contas" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuarios" ("id");

ALTER TABLE "contas" ADD FOREIGN KEY ("banco_id") REFERENCES "bancos" ("id");

ALTER TABLE "categorias" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuarios" ("id");

ALTER TABLE "sub_categorias" ADD FOREIGN KEY ("categoria_id") REFERENCES "categorias" ("id");

ALTER TABLE "sub_categorias" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuarios" ("id");

ALTER TABLE "cartoes" ADD FOREIGN KEY ("conta_id") REFERENCES "contas" ("id");

ALTER TABLE "cartoes" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuarios" ("id");

ALTER TABLE "faturas" ADD FOREIGN KEY ("conta_cartao_id") REFERENCES "cartoes" ("id");

ALTER TABLE "faturas" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuarios" ("id");

ALTER TABLE "transacoes" ADD FOREIGN KEY ("transacao_pai_id") REFERENCES "transacoes" ("id");

ALTER TABLE "transacoes" ADD FOREIGN KEY ("conta_origem_id") REFERENCES "contas" ("id");

ALTER TABLE "transacoes" ADD FOREIGN KEY ("conta_destino_id") REFERENCES "contas" ("id");

ALTER TABLE "transacoes" ADD FOREIGN KEY ("categoria_id") REFERENCES "categorias" ("id");

ALTER TABLE "transacoes" ADD FOREIGN KEY ("sub_categoria_id") REFERENCES "sub_categorias" ("id");

ALTER TABLE "transacoes" ADD FOREIGN KEY ("fatura_id") REFERENCES "faturas" ("id");

ALTER TABLE "transacoes" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuarios" ("id");

ALTER TABLE "transacoes_parcelas" ADD FOREIGN KEY ("transacao_id") REFERENCES "transacoes" ("id");

ALTER TABLE "transacoes_parcelas" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuarios" ("id");
