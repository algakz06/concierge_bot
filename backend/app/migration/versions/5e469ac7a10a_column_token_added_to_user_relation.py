"""column token added to user relation

Revision ID: 5e469ac7a10a
Revises: 4217213b443d
Create Date: 2024-09-24 13:15:27.025331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e469ac7a10a'
down_revision: Union[str, None] = '4217213b443d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscription', sa.Column('token', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscription', 'token')
    # ### end Alembic commands ###
