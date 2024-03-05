"""update action model

Revision ID: d7688034bc8b
Revises: deebc2f9c287
Create Date: 2024-03-05 04:08:49.408603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7688034bc8b'
down_revision = 'deebc2f9c287'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('action',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=140), nullable=False),
    sa.Column('thing_code', sa.String(length=140), nullable=False),
    sa.Column('type', sa.String(length=140), nullable=False),
    sa.Column('destination', sa.String(length=140), nullable=False),
    sa.Column('field', sa.String(length=140), nullable=False),
    sa.Column('operation', sa.String(length=140), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('action')
    # ### end Alembic commands ###