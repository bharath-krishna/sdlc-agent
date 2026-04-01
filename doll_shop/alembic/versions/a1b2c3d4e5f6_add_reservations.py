"""add type and weight to dolls and create reservations table

Revision ID: a1b2c3d4e5f6
Revises: 46f2442485ab
Create Date: 2026-03-30 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '46f2442485ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to dolls
    op.add_column('dolls', sa.Column('type', sa.String(length=50), nullable=False, server_default='wooden'))
    op.add_column('dolls', sa.Column('weight', sa.Float(), nullable=False, server_default='1.0'))
    
    # Create reservations table
    op.create_table('reservations',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('doll_id', sa.String(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['doll_id'], ['dolls.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('reservations')
    op.drop_column('dolls', 'weight')
    op.drop_column('dolls', 'type')
