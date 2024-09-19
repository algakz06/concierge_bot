"""column details added to request table

Revision ID: 4217213b443d
Revises: 0100c97ee241
Create Date: 2024-09-17 08:55:09.215980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4217213b443d'
down_revision: Union[str, None] = '0100c97ee241'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('request', sa.Column('details', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('request', 'details')
    # ### end Alembic commands ###
