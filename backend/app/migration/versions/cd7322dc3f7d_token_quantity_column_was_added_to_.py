"""token_quantity column was added to subscription table

Revision ID: cd7322dc3f7d
Revises: 5e469ac7a10a
Create Date: 2024-09-28 16:06:30.800031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd7322dc3f7d'
down_revision: Union[str, None] = '5e469ac7a10a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscription', sa.Column('token_quantity', sa.Integer(), nullable=False))
    op.drop_column('subscription', 'token')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscription', sa.Column('token', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('subscription', 'token_quantity')
    # ### end Alembic commands ###
