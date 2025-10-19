"""Increase comment column length 256 -> 1024

Revision ID: 20250905_01
Create Date: 2025-09-05

Downgrade warning:
    Shrinking the column back to 256 can cause data loss if any existing
    comment exceeds 256 characters. The downgrade step now performs a
    pre-flight check and aborts with a clear error instead of silently
    truncating or relying on backend defaults. Manually shorten / backup
    offending rows before retrying a downgrade.
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
    conn = op.get_bind()
    tables = ("filmweb_user_watched_movies", "filmweb_user_watched_series")
    
    for table in tables:
        over = conn.execute(sa.text(f"SELECT COUNT(*) FROM {table} WHERE LENGTH(comment) > 256")).scalar()
        if over and over > 0:
            raise RuntimeError(
                f"Cannot downgrade: {over} rows in '{table}' have comment length > 256. "
                "Shorten or archive those rows before retrying."
            )
        
    for table in tables:
        with op.batch_alter_table(table) as batch:
            batch.alter_column(
                "comment",
                existing_type=sa.String(length=1024),
                type_=sa.String(length=256),
                existing_nullable=True,
            )
