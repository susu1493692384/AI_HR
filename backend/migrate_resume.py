"""
简历模型字段更新
添加向量存储相关字段
"""

import asyncio
import sys
sys.path.insert(0, '.')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

async def migrate_resume_table():
    """添加新字段到 resumes 表"""
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ai_hr')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # 检查表是否存在
        result = await db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'resumes'
        """))
        existing_columns = [row[0] for row in result.fetchall()]

        print(f"现有字段: {existing_columns}")

        # 添加新字段
        new_columns = {
            'extracted_text': 'ALTER TABLE resumes ADD COLUMN IF NOT EXISTS extracted_text TEXT',
            'embedding_id': 'ALTER TABLE resumes ADD COLUMN IF NOT EXISTS embedding_id VARCHAR(255)',
            'embedding_model': 'ALTER TABLE resumes ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(100)',
            'candidate_name': 'ALTER TABLE resumes ADD COLUMN IF NOT EXISTS candidate_name VARCHAR(255)',
            'candidate_email': 'ALTER TABLE resumes ADD COLUMN IF NOT EXISTS candidate_email VARCHAR(255)',
            'candidate_phone': 'ALTER TABLE resumes ADD COLUMN IF NOT EXISTS candidate_phone VARCHAR(50)',
            'candidate_location': 'ALTER TABLE resumes ADD COLUMN IF NOT EXISTS candidate_location VARCHAR(255)',
        }

        for col, sql in new_columns.items():
            if col not in existing_columns:
                print(f"添加字段: {col}")
                await db.execute(text(sql))
            else:
                print(f"字段已存在: {col}")

        await db.commit()
        print("数据库迁移完成！")

if __name__ == "__main__":
    asyncio.run(migrate_resume_table())
