"""initial migration

Revision ID: e2b5a069892d
Revises: 
Create Date: 2021-01-09 19:29:23.180354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2b5a069892d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=15), nullable=True),
    sa.Column('password', sa.String(length=80), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('blog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('blog_name', sa.String(length=100), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('followers',
    sa.Column('user-id', sa.Integer(), nullable=True),
    sa.Column('blog-id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['blog-id'], ['blog.id'], ),
    sa.ForeignKeyConstraint(['user-id'], ['user.id'], )
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=True),
    sa.Column('body', sa.String(length=2000), nullable=True),
    sa.Column('author', sa.String(length=20), nullable=True),
    sa.Column('image_name', sa.String(length=100), nullable=True),
    sa.Column('blog_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['blog_id'], ['blog.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('posts')
    op.drop_table('followers')
    op.drop_table('blog')
    op.drop_table('user')
    # ### end Alembic commands ###
