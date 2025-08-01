"""update_chat_message_timestamp_type

Revision ID: 761fc0db81d3
Revises: 0db8c0ab6f26
Create Date: 2025-07-04 11:34:04.180039

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '761fc0db81d3'
down_revision = '0db8c0ab6f26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop the column first and then recreate it with the correct type
    op.drop_column('chatmessage', 'timestamp')
    op.add_column('chatmessage', sa.Column('timestamp', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop the column first and then recreate it with the previous type
    op.drop_column('chatmessage', 'timestamp')
    op.add_column('chatmessage', sa.Column('timestamp', sa.VARCHAR(), nullable=False))
    # ### end Alembic commands ###
