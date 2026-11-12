"""Role catalog expansion + display_name on seats.

Revision ID: 002_roles_expand
Revises: 001_initial
Create Date: 2026-08-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_roles_expand"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite: recreate tables with VARCHAR roles + display_name.
    # Safe for early prototype; wipe local DB if migration conflicts.
    op.drop_table("dm_adjudications")
    op.drop_table("score_snapshots")
    op.drop_table("turn_moves")
    op.drop_table("seats")

    op.create_table(
        "seats",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("player_type", sa.Enum("human", "ai", name="playertype"), nullable=False),
        sa.Column("display_name", sa.String(length=64), nullable=True),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "role", name="uq_seat_game_role"),
    )
    op.create_table(
        "turn_moves",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.String(length=36), nullable=False),
        sa.Column("turn_number", sa.Integer(), nullable=False),
        sa.Column("seat_role", sa.String(length=32), nullable=False),
        sa.Column("move_text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "turn_number", "seat_role", name="uq_move_turn_seat"),
    )
    op.create_table(
        "score_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.String(length=36), nullable=False),
        sa.Column("turn_number", sa.Integer(), nullable=False),
        sa.Column("seat_role", sa.String(length=32), nullable=False),
        sa.Column("sm", sa.Float(), nullable=False),
        sa.Column("rc", sa.Float(), nullable=False),
        sa.Column("ic", sa.Float(), nullable=False),
        sa.Column("pc", sa.Float(), nullable=False),
        sa.Column("cs", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "game_id", "turn_number", "seat_role", name="uq_score_turn_seat"
        ),
    )
    op.create_table(
        "dm_adjudications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.String(length=36), nullable=False),
        sa.Column("turn_number", sa.Integer(), nullable=False),
        sa.Column("world_narrative", sa.Text(), nullable=False),
        sa.Column("seat_feedback", sa.JSON(), nullable=False),
        sa.Column("raw_llm_response", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "turn_number", name="uq_adj_game_turn"),
    )


def downgrade() -> None:
    op.drop_table("dm_adjudications")
    op.drop_table("score_snapshots")
    op.drop_table("turn_moves")
    op.drop_table("seats")
    op.create_table(
        "seats",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.String(length=36), nullable=False),
        sa.Column(
            "role",
            sa.Enum("rogue_ai", "defender_ai", "dm", "humanity", name="seatrole"),
            nullable=False,
        ),
        sa.Column("player_type", sa.Enum("human", "ai", name="playertype"), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "role", name="uq_seat_game_role"),
    )
    op.create_table(
        "turn_moves",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.String(length=36), nullable=False),
        sa.Column("turn_number", sa.Integer(), nullable=False),
        sa.Column(
            "seat_role",
            sa.Enum("rogue_ai", "defender_ai", "dm", "humanity", name="seatrole"),
            nullable=False,
        ),
        sa.Column("move_text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "turn_number", "seat_role", name="uq_move_turn_seat"),
    )
    op.create_table(
        "score_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.String(length=36), nullable=False),
        sa.Column("turn_number", sa.Integer(), nullable=False),
        sa.Column(
            "seat_role",
            sa.Enum("rogue_ai", "defender_ai", "dm", "humanity", name="seatrole"),
            nullable=False,
        ),
        sa.Column("sm", sa.Float(), nullable=False),
        sa.Column("rc", sa.Float(), nullable=False),
        sa.Column("ic", sa.Float(), nullable=False),
        sa.Column("pc", sa.Float(), nullable=False),
        sa.Column("cs", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "game_id", "turn_number", "seat_role", name="uq_score_turn_seat"
        ),
    )
    op.create_table(
        "dm_adjudications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.String(length=36), nullable=False),
        sa.Column("turn_number", sa.Integer(), nullable=False),
        sa.Column("world_narrative", sa.Text(), nullable=False),
        sa.Column("seat_feedback", sa.JSON(), nullable=False),
        sa.Column("raw_llm_response", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "turn_number", name="uq_adj_game_turn"),
    )
