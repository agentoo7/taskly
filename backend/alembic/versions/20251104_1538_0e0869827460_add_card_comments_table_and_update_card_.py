"""add_card_comments_table_and_update_card_activity

Revision ID: 0e0869827460
Revises: 9f081ea649fe
Create Date: 2025-11-04 15:38:02.670640

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0e0869827460'
down_revision = '9f081ea649fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ActivityAction enum type
    activity_action_enum = postgresql.ENUM(
        'created', 'title_changed', 'description_updated', 'moved',
        'assigned', 'unassigned', 'label_added', 'label_removed',
        'due_date_set', 'due_date_cleared', 'priority_changed', 'commented',
        name='activityaction',
        create_type=False
    )
    activity_action_enum.create(op.get_bind(), checkfirst=True)

    # Update card_activities table to use enum instead of string
    op.execute("ALTER TABLE card_activities ALTER COLUMN action TYPE activityaction USING action::activityaction")

    # Create card_comments table
    op.create_table(
        'card_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('card_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('comment_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )

    # Create indexes
    op.create_index('ix_card_comments_id', 'card_comments', ['id'])
    op.create_index('ix_card_comments_card_id', 'card_comments', ['card_id'])
    op.create_index('ix_card_comments_user_id', 'card_comments', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_card_comments_user_id', table_name='card_comments')
    op.drop_index('ix_card_comments_card_id', table_name='card_comments')
    op.drop_index('ix_card_comments_id', table_name='card_comments')

    # Drop card_comments table
    op.drop_table('card_comments')

    # Revert card_activities action column to string
    op.execute("ALTER TABLE card_activities ALTER COLUMN action TYPE varchar(50)")

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS activityaction")
