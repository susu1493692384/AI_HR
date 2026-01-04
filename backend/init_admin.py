import asyncio
import sys
import os
import uuid
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

async def create_admin():
    """创建管理员账户"""

    # 创建数据库连接
    DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ai_hr"
    engine = create_async_engine(DATABASE_URL)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # 启用 pgcrypto 扩展
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
            await session.commit()

            # 先创建表（如果不存在）
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) DEFAULT 'user' NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            await session.commit()

            # 检查管理员是否存在
            result = await session.execute(
                text("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            )
            admin_count = result.scalar()

            if admin_count > 0:
                print("管理员账户已存在")
                return

            # 使用简单的密码哈希（临时方案）
            # 在生产环境中应该使用 bcrypt
            import hashlib
            password = "admin123456"
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # 创建管理员
            admin_id = str(uuid.uuid4())
            await session.execute(text("""
                INSERT INTO users (id, username, email, password_hash, role, is_active, created_at, updated_at)
                VALUES (:id, :username, :email, :password_hash, :role, :is_active, :created_at, :updated_at)
            """), {
                "id": admin_id,
                "username": "admin",
                "email": "admin@ai-hr.com",
                "password_hash": hashed_password,
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

            await session.commit()
            print("管理员账户创建成功！")
            print("用户名: admin")
            print("密码: admin123456")

        except Exception as e:
            print(f"错误: {str(e)}")
            await session.rollback()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_admin())