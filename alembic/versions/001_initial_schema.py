"""Initial schema - Users, Scans, Attacks, RL

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-12-21 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100)),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('last_password_change', sa.DateTime()),
        sa.Column('failed_login_attempts', sa.String(10), default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
    )
    
    # Create scans table
    op.create_table(
        'scans',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('target', sa.String(255), nullable=False, index=True),
        sa.Column('scan_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('ports', sa.String(255)),
        sa.Column('options', sa.JSON()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('progress', sa.Integer(), default=0),
        sa.Column('results', sa.JSON()),
        sa.Column('error', sa.Text()),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
    )
    
    # Create attacks table
    op.create_table(
        'attacks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('target', sa.String(500), nullable=False, index=True),
        sa.Column('attack_type', sa.String(50), nullable=False, index=True),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('parameters', sa.JSON()),
        sa.Column('use_rl', sa.Boolean(), default=True),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('progress', sa.Integer(), default=0),
        sa.Column('results', sa.JSON()),
        sa.Column('error', sa.Text()),
        sa.Column('rl_episode_id', sa.String(36), index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
    )
    
    # Create rl_episodes table
    op.create_table(
        'rl_episodes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('agent_type', sa.String(50), nullable=False, index=True),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('total_reward', sa.Float(), default=0.0),
        sa.Column('steps', sa.Integer(), default=0),
        sa.Column('success_rate', sa.Float(), default=0.0),
        sa.Column('initial_state', sa.JSON()),
        sa.Column('final_state', sa.JSON()),
        sa.Column('actions', sa.JSON()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('metadata', sa.JSON()),
        sa.Column('error', sa.Text()),
        sa.Column('attack_id', sa.String(36), index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
    )
    
    # Create rl_experiences table
    op.create_table(
        'rl_experiences',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('episode_id', sa.String(36), nullable=False, index=True),
        sa.Column('agent_type', sa.String(50), nullable=False, index=True),
        sa.Column('state', sa.JSON(), nullable=False),
        sa.Column('action', sa.JSON(), nullable=False),
        sa.Column('reward', sa.Float(), nullable=False),
        sa.Column('next_state', sa.JSON(), nullable=False),
        sa.Column('done', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
    )
    
    # Create rl_models table
    op.create_table(
        'rl_models',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('agent_type', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('trained_episodes', sa.Integer(), default=0),
        sa.Column('avg_reward', sa.Float(), default=0.0),
        sa.Column('success_rate', sa.Float(), default=0.0),
        sa.Column('model_path', sa.String(500)),
        sa.Column('file_size_mb', sa.Float()),
        sa.Column('metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
    )
    
    # Create indexes
    op.create_index('idx_scans_user_status', 'scans', ['user_id', 'status'])
    op.create_index('idx_attacks_user_status', 'attacks', ['user_id', 'status'])
    op.create_index('idx_rl_episodes_agent_status', 'rl_episodes', ['agent_type', 'status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_rl_episodes_agent_status')
    op.drop_index('idx_attacks_user_status')
    op.drop_index('idx_scans_user_status')
    
    # Drop tables
    op.drop_table('rl_models')
    op.drop_table('rl_experiences')
    op.drop_table('rl_episodes')
    op.drop_table('attacks')
    op.drop_table('scans')
    op.drop_table('users')
