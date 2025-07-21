"""adiciona coluna dados input em contas_correntes

Revision ID: 8a4860fa0832
Revises: 90da5d644b34
Create Date: 2025-07-21 18:16:20.111928

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "8a4860fa0832"
down_revision: str | Sequence[str] | None = "90da5d644b34"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
