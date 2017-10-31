"""empty message

Revision ID: 3dd8a72e1a2b
Revises: 4170e3b7e7f7
Create Date: 2017-10-31 11:01:28.171029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3dd8a72e1a2b'
down_revision = '4170e3b7e7f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_tickets_type', table_name='tickets')
    op.drop_column('tickets', 'type')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tickets', sa.Column('type', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    op.create_index('ix_tickets_type', 'tickets', ['type'], unique=False)
    # ### end Alembic commands ###
