"""Add ending type and epilogue to games.

Revision ID: 004_ending_epilogue
Revises: 003_world_state_digest
Create Date: 2026-11-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_ending_epilogue"
down_revision: Union[str, None] = "003_world_state_digest"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("games") as batch:
        batch.add_column(sa.Column("ending", sa.String(length=32), nullable=True))
        batch.add_column(sa.Column("epilogue", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("games") as batch:
        batch.drop_column("epilogue")
        batch.drop_column("ending")
