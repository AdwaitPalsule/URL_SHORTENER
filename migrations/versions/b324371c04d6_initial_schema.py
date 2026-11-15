"""initial schema

Revision ID: b324371c04d6
Revises:
Create Date: 2026-10-27 20:19:46.333992
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b324371c04d6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("original_url", sa.String(), nullable=False),
        sa.Column("short_code", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("short_code"),
    )
    op.create_index(
        op.f("ix_links_short_code"),
        "links",
        ["short_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_links_short_code"), table_name="links")
    op.drop_table("links")