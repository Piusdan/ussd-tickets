"""empty message

Revision ID: 4170e3b7e7f7
Revises: 9934fb768805
Create Date: 2017-10-31 10:55:09.685881

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4170e3b7e7f7'
down_revision = '9934fb768805'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ticket_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_ticket_types_default'), 'ticket_types', ['default'], unique=False)
    op.drop_column(u'events', 'filename')
    op.add_column(u'tickets', sa.Column('type_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tickets', 'ticket_types', ['type_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tickets', type_='foreignkey')
    op.drop_column(u'tickets', 'type_id')
    op.add_column(u'events', sa.Column('filename', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_ticket_types_default'), table_name='ticket_types')
    op.drop_table('ticket_types')
    # ### end Alembic commands ###