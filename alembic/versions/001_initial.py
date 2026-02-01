"""Initial migration - Create documents and chunks tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-01 17:12:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('upload_date', sa.DateTime(), nullable=True),
        sa.Column('processing_status', sa.String(), nullable=True),
        sa.Column('doc_metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on upload_date for faster queries
    op.create_index(
        'ix_documents_upload_date',
        'documents',
        ['upload_date'],
        unique=False
    )
    
    # Create index on processing_status
    op.create_index(
        'ix_documents_status',
        'documents',
        ['processing_status'],
        unique=False
    )
    
    # Create chunks table
    op.create_table(
        'chunks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('chunk_type', sa.String(), nullable=True),
        sa.Column('tokens', sa.Integer(), nullable=True),
        sa.Column('start_pos', sa.Integer(), nullable=True),
        sa.Column('end_pos', sa.Integer(), nullable=True),
        sa.Column('chunk_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on document_id for faster lookups
    op.create_index(
        'ix_chunks_document_id',
        'chunks',
        ['document_id'],
        unique=False
    )
    
    # Create index on chunk_index for ordering
    op.create_index(
        'ix_chunks_index',
        'chunks',
        ['chunk_index'],
        unique=False
    )
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_chunks_document_id',
        'chunks',
        'documents',
        ['document_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Drop all tables."""
    
    # Drop foreign key first
    op.drop_constraint('fk_chunks_document_id', 'chunks', type_='foreignkey')
    
    # Drop indexes
    op.drop_index('ix_chunks_index', table_name='chunks')
    op.drop_index('ix_chunks_document_id', table_name='chunks')
    op.drop_index('ix_documents_status', table_name='documents')
    op.drop_index('ix_documents_upload_date', table_name='documents')
    
    # Drop tables
    op.drop_table('chunks')
    op.drop_table('documents')
