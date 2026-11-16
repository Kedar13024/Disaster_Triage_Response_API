"""Add user accounts and optional incident reporters.

Revision ID: 04f97b6cdf79
Revises: dcf9a8ff3bdd
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "04f97b6cdf79"
down_revision: Union[str, Sequence[str], None] = "dcf9a8ff3bdd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = sa.Enum("citizen", "responder", "admin", name="user_role")
    user_role.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_fullname", sa.String(length=50), nullable=False),
        sa.Column("user_phoneno", sa.String(length=20), nullable=False),
        sa.Column("user_email", sa.String(), nullable=False, unique=True),
        sa.Column("user_password", sa.String(), nullable=False),
        sa.Column("user_role", user_role, nullable=False, server_default="citizen"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.add_column("incidents", sa.Column("reported_by", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_incidents_reported_by_users",
        "incidents",
        "users",
        ["reported_by"],
        ["user_id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_incidents_reported_by_users", "incidents", type_="foreignkey")
    op.drop_column("incidents", "reported_by")
    op.drop_table("users")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
