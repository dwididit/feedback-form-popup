from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'de2ff3619e21'
down_revision = '5704a05ce4eb'
branch_labels = None
depends_on = None

def upgrade():
    # Add columns with default values to avoid NOT NULL constraint violations
    op.add_column('feedback', sa.Column('full_name', sa.String(), nullable=False, server_default='Unknown'))
    op.add_column('feedback', sa.Column('email', sa.String(), nullable=False, server_default='unknown@example.com'))
    # Remove server defaults after adding the columns
    op.alter_column('feedback', 'full_name', server_default=None)
    op.alter_column('feedback', 'email', server_default=None)

def downgrade():
    op.drop_column('feedback', 'email')
    op.drop_column('feedback', 'full_name')
