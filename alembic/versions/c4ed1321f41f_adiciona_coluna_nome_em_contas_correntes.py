"""adiciona coluna nome em contas_correntes

Revision ID: c4ed1321f41f
Revises: cfb1c942704a
Create Date: 2025-07-21 11:16:58.775771

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4ed1321f41f"
down_revision: str | Sequence[str] | None = "cfb1c942704a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


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
