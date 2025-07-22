"""adiciona coluna nome em contas_correntes

Revision ID: 1234abcd5678
Revises: id_da_migracao_anterior
Create Date: 2025-07-20 20:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# IDs de versão Alembic
revision = "1234abcd5678"  # ID único desta migração
down_revision = "id_da_migracao_anterior"  # Substitua pelo revision ID anterior
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Adiciona a coluna como nullable=True
    op.add_column(
        "contas_correntes", sa.Column("nome", sa.String(length=100), nullable=True)
    )

    # 2. Preenche todos os registros existentes com valor padrão
    op.execute("UPDATE contas_correntes SET nome = 'Conta Padrão' WHERE nome IS NULL")

    # 3. Altera para nullable=False
    op.alter_column("contas_correntes", "nome", nullable=False)


def downgrade() -> None:
    # Remove a coluna na reversão
    op.drop_column("contas_correntes", "nome")
