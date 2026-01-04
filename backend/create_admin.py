"""创建管理员账户的简单脚本"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.security import get_password_hash
from app.infrastructure.database.models import User


async def create_admin():
    """创建管理员账户"""

    # 创建数据库连接
    engine = create_async_engine(settings.DATABASE_URL)

    # 创建会话
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # 检查是否已存在管理员
            result = await session.execute(
                select(User).where(User.role == 'admin')
            )
            existing_admin = result.scalar_one_or_none()

            if existing_admin:
                print("[OK] Admin account already exists")
                print(f"   Username: {existing_admin.username}")
                print(f"   Email: {existing_admin.email}")
                print("   Password: admin123 (default)")
                return

            # 创建新管理员
            admin_password = "admin123"
            hashed_password = get_password_hash(admin_password)

            new_admin = User(
                username="admin",
                email="admin@ai-hr.com",
                password_hash=hashed_password,
                role="admin",
                is_active=True
            )

            session.add(new_admin)
            await session.commit()

            print("[OK] Admin account created successfully!")
            print("=" * 40)
            print(f"Username: admin")
            print(f"Email: admin@ai-hr.com")
            print(f"Password: {admin_password}")
            print("=" * 40)
            print("Please change the password after login!")

        except Exception as e:
            print(f"[ERROR] Create failed: {str(e)}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin())