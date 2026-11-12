"""Add world_state_digest to dm_adjudications for rolling Narrator memory.

Revision ID: 003_world_state_digest
Revises: 002_roles_expand
Create Date: 2026-08-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_world_state_digest"
down_revision: Union[str, None] = "002_roles_expand"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dm_adjudications") as batch:
        batch.add_column(
            sa.Column(
                "world_state_digest",
                sa.Text(),
                nullable=False,
                server_default="",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("dm_adjudications") as batch:
        batch.drop_column("world_state_digest")
