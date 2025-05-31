"""add_practice_session_models_and_question_year_field

Revision ID: 164a81a067be
Revises: 2d7418ee59e3
Create Date: 2025-05-31 21:34:06.518030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '164a81a067be'
down_revision: Union[str, None] = '2d7418ee59e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
