"""increase_chat_message_content_length

Revision ID: 7c3ae6534636
Revises: 761fc0db81d3
Create Date: 2025-07-04 12:17:33.100203

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '7c3ae6534636'
down_revision = '761fc0db81d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chatmessage', 'content',
               existing_type=sa.VARCHAR(length=2000),
               type_=sqlmodel.sql.sqltypes.AutoString(length=5000),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chatmessage', 'content',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=5000),
               type_=sa.VARCHAR(length=2000),
               existing_nullable=False)
    # ### end Alembic commands ###
