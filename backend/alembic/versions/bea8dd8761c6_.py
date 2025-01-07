"""empty message

Revision ID: bea8dd8761c6
Revises: adffc978038d, b1e84d34320e
Create Date: 2024-12-25 19:31:19.487593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bea8dd8761c6'
down_revision: Union[str, None] = ('adffc978038d', 'b1e84d34320e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
