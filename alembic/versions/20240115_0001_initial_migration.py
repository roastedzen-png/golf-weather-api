"""Initial migration - create usage tracking tables

Revision ID: 0001
Revises:
Create Date: 2024-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create api_usage table
    op.create_table(
        'api_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.String(length=50), nullable=False),
        sa.Column('endpoint', sa.String(length=100), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('request_count', sa.Integer(), default=0),
        sa.Column('error_count', sa.Integer(), default=0),
        sa.Column('total_latency_ms', sa.Float(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_api_usage_id', 'api_usage', ['id'], unique=False)
    op.create_index('ix_api_usage_client_id', 'api_usage', ['client_id'], unique=False)
    op.create_index('ix_api_usage_date', 'api_usage', ['date'], unique=False)
    op.create_index('ix_usage_client_date', 'api_usage', ['client_id', 'date'], unique=False)
    op.create_index('ix_usage_client_endpoint_date', 'api_usage', ['client_id', 'endpoint', 'date'], unique=True)

    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.String(length=50), nullable=False),
        sa.Column('key_hash', sa.String(length=64), nullable=False),
        sa.Column('tier', sa.String(length=20), default='standard'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('last_used_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id')
    )
    op.create_index('ix_api_keys_id', 'api_keys', ['id'], unique=False)
    op.create_index('ix_api_keys_client_id', 'api_keys', ['client_id'], unique=True)

    # Create request_logs table
    op.create_table(
        'request_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.String(length=36), nullable=False),
        sa.Column('client_id', sa.String(length=50), nullable=False),
        sa.Column('endpoint', sa.String(length=100), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_id')
    )
    op.create_index('ix_request_logs_id', 'request_logs', ['id'], unique=False)
    op.create_index('ix_request_logs_request_id', 'request_logs', ['request_id'], unique=True)
    op.create_index('ix_request_logs_client_id', 'request_logs', ['client_id'], unique=False)
    op.create_index('ix_request_logs_created_at', 'request_logs', ['created_at'], unique=False)
    op.create_index('ix_logs_client_created', 'request_logs', ['client_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('request_logs')
    op.drop_table('api_keys')
    op.drop_table('api_usage')
