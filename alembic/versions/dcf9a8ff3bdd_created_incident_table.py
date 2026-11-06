"""Create the incidents table.

Revision ID: dcf9a8ff3bdd
Revises: 
Create Date: 2026-11-06 13:49:04.734892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcf9a8ff3bdd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the table used to store reported incidents."""

    op.create_table(
        "incidents",
        # Use an integer primary key to identify each incident.
        sa.Column("incident_id", sa.Integer(), primary_key=True, nullable=False),
        # Require the incident category and reporter-provided description.
        sa.Column("incident_type", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        # Default new incidents to low severity and make them publicly visible.
        sa.Column("severity", sa.String(), nullable=False, server_default="low"),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column(
            "reported_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    """Remove the incidents table created by this revision."""
    op.drop_table("incidents")
