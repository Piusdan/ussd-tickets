"""empty message

Revision ID: 62cc3cb59048
Revises: 6cab8cc1f8ff
Create Date: 2017-12-28 10:26:38.951865

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62cc3cb59048'
down_revision = '6cab8cc1f8ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sms_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('message_id', sa.String(), nullable=True),
    sa.Column('susbscription_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['susbscription_id'], ['subscriptions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sms_logs_status'), 'sms_logs', ['status'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sms_logs_status'), table_name='sms_logs')
    op.drop_table('sms_logs')
    # ### end Alembic commands ###
