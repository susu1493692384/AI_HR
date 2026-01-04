"""
修复用户租户模型配置脚本
将模型配置从默认租户复制到用户租户
"""
import asyncio
import sys
import os

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ai_hr"
DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"

async def get_user_tenant_id(session: AsyncSession) -> str:
    """获取第一个用户ID作为租户ID"""
    result = await session.execute(text("SELECT id FROM users LIMIT 1"))
    user = result.fetchone()
    return user[0] if user else None

async def copy_models_to_user_tenant():
    """复制模型配置到用户租户"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # 1. 获取用户租户ID
            user_tenant_id = await get_user_tenant_id(session)
            if not user_tenant_id:
                print("[ERROR] User not found")
                return

            print(f"[INFO] User Tenant ID: {user_tenant_id}")
            print(f"[INFO] Default Tenant ID: {DEFAULT_TENANT_ID}")

            # 2. 查询默认租户的所有模型配置
            result = await session.execute(
                text("""
                    SELECT llm_factory, llm_name, model_type, api_key, api_base, max_tokens
                    FROM tenant_llm
                    WHERE tenant_id = :default_tenant
                """),
                {"default_tenant": DEFAULT_TENANT_ID}
            )
            default_models = result.fetchall()

            if not default_models:
                print("[ERROR] No model configuration found in default tenant")
                return

            print(f"\n[INFO] Found {len(default_models)} model configuration(s)")

            # 3. 删除用户租户下的旧配置
            await session.execute(
                text("DELETE FROM tenant_llm WHERE tenant_id = :user_tenant"),
                {"user_tenant": user_tenant_id}
            )
            print("[INFO] Cleared old user tenant configuration")

            # 4. 复制模型配置到用户租户
            for model in default_models:
                await session.execute(
                    text("""
                        INSERT INTO tenant_llm
                        (tenant_id, llm_factory, model_type, llm_name, api_key, api_base, max_tokens, used_tokens, status)
                        VALUES (:tenant_id, :llm_factory, :model_type, :llm_name, :api_key, :api_base, :max_tokens, 0, '1')
                    """),
                    {
                        "tenant_id": user_tenant_id,
                        "llm_factory": model[0],
                        "model_type": model[2],
                        "llm_name": model[1],
                        "api_key": model[3],
                        "api_base": model[4],
                        "max_tokens": model[5]
                    }
                )
                print(f"[OK] Copied model: {model[0]} - {model[1]}")

            # 5. 更新用户租户的默认模型设置
            await session.execute(
                text("""
                    UPDATE tenants
                    SET llm_id = 'glm-4@ZHIPU-AI'
                    WHERE id = :user_tenant
                """),
                {"user_tenant": user_tenant_id}
            )
            print("\n[INFO] Updated default chat model to: glm-4@ZHIPU-AI")

            # 6. 提交更改
            await session.commit()
            print("\n[SUCCESS] Configuration fixed successfully!")

            # 7. 验证配置
            print("\n[INFO] Verification:")
            result = await session.execute(
                text("""
                    SELECT t.id, t.name, t.llm_id
                    FROM tenants t
                    WHERE t.id = :user_tenant
                """),
                {"user_tenant": user_tenant_id}
            )
            tenant = result.fetchone()
            if tenant:
                print(f"  Tenant ID: {tenant[0]}")
                print(f"  Tenant Name: {tenant[1]}")
                print(f"  Default Model: {tenant[2]}")

            result = await session.execute(
                text("""
                    SELECT llm_factory, llm_name
                    FROM tenant_llm
                    WHERE tenant_id = :user_tenant
                """),
                {"user_tenant": user_tenant_id}
            )
            models = result.fetchall()
            print(f"\n  Configured models ({len(models)} total):")
            for m in models:
                print(f"    - {m[0]}: {m[1]}")

            print("\n[SUCCESS] You can now use the chat feature in AI Analysis Assistant!")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("Fix User Tenant Model Configuration")
    print("=" * 60)
    asyncio.run(copy_models_to_user_tenant())
