"""drop_doctors_table

Revision ID: 640d2162a405
Revises: 1e6b7927b28f
Create Date: 2026-01-11 19:52:56.495934

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "640d2162a405"
down_revision: str | Sequence[str] | None = "1e6b7927b28f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Drop doctors table - no longer needed for server-to-server auth."""
    op.drop_table("doctors")


def downgrade() -> None:
    """Downgrade not supported - this is a one-way migration."""
    pass
