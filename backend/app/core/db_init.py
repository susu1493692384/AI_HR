"""数据库初始化脚本"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.infrastructure.database.database import get_async_session
from app.core.security import get_password_hash


async def create_default_admin():
    """创建默认管理员账户"""
    async for db in get_async_session():
        # 检查是否已存在管理员
        result = await db.execute(
            text("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        )
        admin_count = result.scalar()

        if admin_count > 0:
            print("管理员账户已存在，跳过创建")
            return

        # 创建默认管理员
        admin_password = "admin123456"  # 默认密码，首次登录后建议修改
        hashed_password = get_password_hash(admin_password)

        await db.execute(
            text("""
                INSERT INTO users (username, email, password_hash, role, is_active, created_at, updated_at)
                VALUES (:username, :email, :password_hash, :role, :is_active, NOW(), NOW())
            """),
            {
                "username": "admin",
                "email": "admin@ai-hr.com",
                "password_hash": hashed_password,
                "role": "admin",
                "is_active": True,
            }
        )

        await db.commit()
        print(f"默认管理员账户创建成功！")
        print(f"用户名: admin")
        print(f"邮箱: admin@ai-hr.com")
        print(f"密码: {admin_password}")
        print("请登录后立即修改密码！")


async def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")

    # 创建默认管理员
    await create_default_admin()

    print("数据库初始化完成！")


if __name__ == "__main__":
    asyncio.run(init_database())