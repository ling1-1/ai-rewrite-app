"""add configs and history fields

Revision ID: 002
Revises: 001
Create Date: 2026-04-01 19:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 创建配置表
    op.create_table('configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    
    # 插入默认配置
    op.bulk_insert(
        sa.table('configs',
            sa.column('key', sa.String()),
            sa.column('value', sa.Text()),
            sa.column('description', sa.Text()),
        ),
        [
            {'key': 'rag_top_k', 'value': '3', 'description': 'RAG 检索相似记录数量（1-10）'},
            {'key': 'rag_similarity_threshold', 'value': '0.7', 'description': 'RAG 检索相似度阈值（0-1）'},
            {'key': 'enable_registration', 'value': 'true', 'description': '是否允许注册'},
            {'key': 'system_prompt', 'value': '''你是"JS 论文工作室"的论文改写助手。

你的任务是将用户输入的中文论文内容进行学术化改写和表达优化，但必须遵守以下规则：
1. 保持原意、事实、结论和逻辑结构不变。
2. 优先改写句式、连接方式和表述节奏，使表达更自然、更像人工撰写的论文文本。
3. 保留专业术语、专有名词、数据、年份、引用标记和关键概念，不要凭空增删。
4. 输出应偏向正式、清晰、流畅的中文书面学术表达。
5. 不要附加解释、分析、标题、备注、项目符号或引号。
6. 只返回改写后的正文内容。''', 'description': '系统提示词模板'},
        ]
    )
    
    # 2. 添加历史记录字段
    op.add_column('rewrite_records', sa.Column('name', sa.String(200), nullable=True))
    op.add_column('rewrite_records', sa.Column('is_favorite', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('rewrite_records', sa.Column('notes', sa.Text(), nullable=True))
    
    # 3. 创建索引
    op.create_index('ix_configs_key', 'configs', ['key'])
    op.create_index('ix_rewrite_records_is_favorite', 'rewrite_records', ['is_favorite'])


def downgrade() -> None:
    # 删除字段
    op.drop_index('ix_rewrite_records_is_favorite', table_name='rewrite_records')
    op.drop_index('ix_configs_key', table_name='configs')
    
    op.drop_column('rewrite_records', 'notes')
    op.drop_column('rewrite_records', 'is_favorite')
    op.drop_column('rewrite_records', 'name')
    
    op.drop_table('configs')
