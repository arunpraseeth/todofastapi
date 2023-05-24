"""create address _id to users

Revision ID: 2ffdf7fb6889
Revises: 3a913aa07ecd
Create Date: 2023-05-03 19:10:55.361834

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ffdf7fb6889'
down_revision = '3a913aa07ecd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("address_id", sa.Integer(), nullable=True))
    op.create_foreign_key("address_users_fk",
                          source_table="users",
                          referent_table="address",
                          local_cols=["address_id"],
                          remote_cols=["id"],
                          ondelete="CASCADE"
                          )


def downgrade():
    op.drop_constraint("address_users_fk", table_name="users")
    op.drop_column(table_name="users", column_name="address_id")
