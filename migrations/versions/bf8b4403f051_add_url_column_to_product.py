"""Add url column to product

Revision ID: bf8b4403f051
Revises: 
Create Date: 2023-10-10 07:29:20.906065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf8b4403f051'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('url', sa.Text(), nullable=False))
        batch_op.create_unique_constraint(None, ['url'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('url')

    # ### end Alembic commands ###
