"""add appartment number column

Revision ID: c1d9b1dfd4e1
Revises: 2ffdf7fb6889
Create Date: 2023-05-09 00:00:09.786293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1d9b1dfd4e1'
down_revision = '2ffdf7fb6889'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('address', sa.Column('apt_num', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('address', 'apt_num')
