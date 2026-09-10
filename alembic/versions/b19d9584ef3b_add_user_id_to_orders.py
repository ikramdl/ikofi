"""Add user_id to orders

Revision ID: b19d9584ef3b
Revises: 6406e9a2dfc3
Create Date: 2026-09-08 21:00:27.249944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b19d9584ef3b'
down_revision: Union[str, Sequence[str], None] = '6406e9a2dfc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'orders',
        sa.Column('user_id', sa.Integer(), nullable=False)
    )
    op.create_foreign_key(
        None,
        'orders',
        'users',
        ['user_id'],
        ['id']
    )

def downgrade() -> None:
    op.drop_constraint(None, 'orders', type_='foreignkey')
    op.drop_column('orders', 'user_id')