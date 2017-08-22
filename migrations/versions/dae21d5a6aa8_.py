"""empty message

Revision ID: dae21d5a6aa8
Revises: 6a403f957c70
Create Date: 2017-08-17 08:13:56.495573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dae21d5a6aa8'
down_revision = '6a403f957c70'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('purchases', sa.Column('url', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('purchases', 'url')
    # ### end Alembic commands ###