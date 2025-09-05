"""Increase comment column length 256 -> 1024

Revision ID: 20250905_01
Create Date: 2025-09-05
"""

from alembic import op
import sqlalchemy as sa

# revision for alembic
revision = "20250905_01"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    for table in ("filmweb_user_watched_movies", "filmweb_user_watched_series"):
        with op.batch_alter_table(table) as batch:
            batch.alter_column(
                "comment",
                existing_type=sa.String(length=256),
                type_=sa.String(length=1024),
                existing_nullable=True,
            )


def downgrade():
    for table in ("filmweb_user_watched_movies", "filmweb_user_watched_series"):
        with op.batch_alter_table(table) as batch:
            batch.alter_column(
                "comment",
                existing_type=sa.String(length=1024),
                type_=sa.String(length=256),
                existing_nullable=True,
            )
