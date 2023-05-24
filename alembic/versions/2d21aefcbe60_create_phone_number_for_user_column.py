"""create phone number for user column

Revision ID: 2d21aefcbe60
Revises: 
Create Date: 2023-05-03 17:20:13.202175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d21aefcbe60'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'phone_number')
