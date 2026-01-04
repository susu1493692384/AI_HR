"""
添加 uploaded_by 字段到 resumes 表
运行方式: python add_uploaded_by_field.py
"""

import asyncio
from sqlalchemy import text
from app.infrastructure.database.database import engine


async def add_uploaded_by_field():
    """添加 uploaded_by 字段"""
    async with engine.begin() as conn:
        try:
            # 检查字段是否已存在
            result = await conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'resumes'
                AND column_name = 'uploaded_by'
            """))

            if result.fetchone():
                print("✅ uploaded_by 字段已存在，无需添加")
                return

            # 添加字段
            print("📝 正在添加 uploaded_by 字段...")
            await conn.execute(text("""
                ALTER TABLE resumes
                ADD COLUMN uploaded_by UUID NULL
            """))
            print("✅ 字段添加成功")

            # 添加外键约束
            print("📝 正在添加外键约束...")
            await conn.execute(text("""
                ALTER TABLE resumes
                ADD CONSTRAINT fk_resumes_uploaded_by
                FOREIGN KEY (uploaded_by)
                REFERENCES users(id)
            """))
            print("✅ 外键约束添加成功")

            # 创建索引
            print("📝 正在创建索引...")
            await conn.execute(text("""
                CREATE INDEX ix_resumes_uploaded_by
                ON resumes(uploaded_by)
            """))
            print("✅ 索引创建成功")

            print("\n🎉 数据库迁移完成！")

        except Exception as e:
            print(f"❌ 迁移失败: {str(e)}")
            raise


if __name__ == "__main__":
    print("开始数据库迁移...\n")
    asyncio.run(add_uploaded_by_field())
