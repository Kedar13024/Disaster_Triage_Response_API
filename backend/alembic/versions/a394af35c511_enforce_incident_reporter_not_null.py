"""enforce incident reporter not null

Revision ID: a394af35c511
Revises: 04f97b6cdf79
Create Date: 2026-11-20 12:59:13.588532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a394af35c511'
down_revision: Union[str, Sequence[str], None] = '04f97b6cdf79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enforce non-null incident reporters."""
    op.alter_column(
        "incidents",
        "reported_by",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    """Allow null incident reporters again."""
    op.alter_column(
        "incidents",
        "reported_by",
        existing_type=sa.Integer(),
        nullable=True,
    )