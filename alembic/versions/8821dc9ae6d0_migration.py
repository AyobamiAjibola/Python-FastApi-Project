"""migration

Revision ID: 8821dc9ae6d0
Revises: 5245b262af5c
Create Date: 2024-11-12 17:35:18.013008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8821dc9ae6d0'
down_revision: Union[str, None] = '5245b262af5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('restaurant_user_id_fkey', 'restaurant', type_='foreignkey')
    op.drop_column('restaurant', 'user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('restaurant', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('restaurant_user_id_fkey', 'restaurant', 'restaurant_user', ['user_id'], ['id'])
    # ### end Alembic commands ###
