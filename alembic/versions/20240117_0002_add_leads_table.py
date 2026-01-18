"""Add leads table for lead management

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create leads table
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False),

        # Lead Source
        sa.Column('source', sa.String(length=50), nullable=False),  # 'api_key_request', 'contact_form', 'newsletter'

        # Contact Information
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=True),

        # API Key Request Specific
        sa.Column('use_case', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('expected_volume', sa.String(length=50), nullable=True),
        sa.Column('api_key_id', sa.Integer(), sa.ForeignKey('api_keys.id'), nullable=True),

        # Contact Form Specific
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),

        # Lead Quality
        sa.Column('is_high_value', sa.Boolean(), default=False),
        sa.Column('priority', sa.String(length=20), default='normal'),  # 'low', 'normal', 'high', 'urgent'

        # Status Tracking
        sa.Column('status', sa.String(length=50), default='new'),  # 'new', 'contacted', 'qualified', 'converted', 'lost'
        sa.Column('assigned_to', sa.String(length=255), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.Column('contacted_at', sa.DateTime(timezone=True), nullable=True),

        # Notes
        sa.Column('internal_notes', sa.Text(), nullable=True),

        # Metadata
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('referrer', sa.String(length=500), nullable=True),

        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('ix_leads_id', 'leads', ['id'], unique=False)
    op.create_index('ix_leads_source', 'leads', ['source'], unique=False)
    op.create_index('ix_leads_email', 'leads', ['email'], unique=False)
    op.create_index('ix_leads_status', 'leads', ['status'], unique=False)
    op.create_index('ix_leads_is_high_value', 'leads', ['is_high_value'], unique=False)
    op.create_index('ix_leads_created_at', 'leads', ['created_at'], unique=False)

    # Composite index for common queries
    op.create_index('ix_leads_source_status', 'leads', ['source', 'status'], unique=False)

    # Add extra columns to api_keys table for lead capture data
    op.add_column('api_keys', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('api_keys', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('api_keys', sa.Column('company', sa.String(length=255), nullable=True))
    op.add_column('api_keys', sa.Column('use_case', sa.String(length=255), nullable=True))
    op.add_column('api_keys', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('api_keys', sa.Column('expected_volume', sa.String(length=50), nullable=True))
    op.add_column('api_keys', sa.Column('status', sa.String(length=20), server_default='active'))

    # Add email index on api_keys
    op.create_index('ix_api_keys_email', 'api_keys', ['email'], unique=False)


def downgrade() -> None:
    # Drop email index from api_keys
    op.drop_index('ix_api_keys_email', table_name='api_keys')

    # Remove columns from api_keys
    op.drop_column('api_keys', 'status')
    op.drop_column('api_keys', 'expected_volume')
    op.drop_column('api_keys', 'description')
    op.drop_column('api_keys', 'use_case')
    op.drop_column('api_keys', 'company')
    op.drop_column('api_keys', 'email')
    op.drop_column('api_keys', 'name')

    # Drop leads table indexes
    op.drop_index('ix_leads_source_status', table_name='leads')
    op.drop_index('ix_leads_created_at', table_name='leads')
    op.drop_index('ix_leads_is_high_value', table_name='leads')
    op.drop_index('ix_leads_status', table_name='leads')
    op.drop_index('ix_leads_email', table_name='leads')
    op.drop_index('ix_leads_source', table_name='leads')
    op.drop_index('ix_leads_id', table_name='leads')

    # Drop leads table
    op.drop_table('leads')
