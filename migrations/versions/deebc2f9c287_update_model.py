"""update model

Revision ID: deebc2f9c287
Revises: b2defa2d6b9b
Create Date: 2024-03-04 15:56:36.948714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'deebc2f9c287'
down_revision = 'b2defa2d6b9b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gas', sa.Float(), nullable=False))
        batch_op.drop_column('speed')

    with op.batch_alter_table('thing', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location_name', sa.String(length=140), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('thing', schema=None) as batch_op:
        batch_op.drop_column('location_name')

    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('speed', sa.FLOAT(), nullable=False))
        batch_op.drop_column('gas')

    # ### end Alembic commands ###