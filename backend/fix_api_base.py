"""
修复智谱AI的API Base URL
"""
import asyncio
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ai_hr"

async def fix_api_base():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # 获取用户租户ID
            result = await session.execute(text("SELECT id FROM users LIMIT 1"))
            user = result.fetchone()
            if not user:
                print("[ERROR] No user found")
                return
            user_tenant_id = user[0]

            print(f"[INFO] User Tenant ID: {user_tenant_id}")

            # 检查当前配置
            result = await session.execute(
                text("""
                    SELECT llm_factory, llm_name, api_base
                    FROM tenant_llm
                    WHERE tenant_id = :user_tenant
                      AND llm_factory = 'ZHIPU-AI'
                """),
                {"user_tenant": user_tenant_id}
            )
            configs = result.fetchall()

            print(f"\n[INFO] Found {len(configs)} ZHIPU-AI model(s)")

            # 更新所有智谱AI模型的API Base
            zhipu_api_base = "https://open.bigmodel.cn/api/paas/v4"

            updated_count = 0
            for config in configs:
                factory, model_name, current_base = config
                print(f"\n  Model: {model_name}")
                print(f"  Current API Base: {current_base or '(EMPTY)'}")

                # 更新API Base
                await session.execute(
                    text("""
                        UPDATE tenant_llm
                        SET api_base = :api_base
                        WHERE tenant_id = :tenant_id
                          AND llm_factory = :factory
                          AND llm_name = :model_name
                    """),
                    {
                        "tenant_id": user_tenant_id,
                        "factory": factory,
                        "model_name": model_name,
                        "api_base": zhipu_api_base
                    }
                )
                updated_count += 1
                print(f"  -> Updated to: {zhipu_api_base}")

            await session.commit()
            print(f"\n[SUCCESS] Updated {updated_count} model(s)")

            # 验证更新
            result = await session.execute(
                text("""
                    SELECT llm_name, api_base
                    FROM tenant_llm
                    WHERE tenant_id = :user_tenant
                      AND llm_factory = 'ZHIPU-AI'
                      AND llm_name = 'glm-4'
                """),
                {"user_tenant": user_tenant_id}
            )
            glm4_config = result.fetchone()

            if glm4_config:
                print(f"\n[INFO] GLM-4 Verification:")
                print(f"  Model: {glm4_config[0]}")
                print(f"  API Base: {glm4_config[1]}")
                print("\n[SUCCESS] Configuration is now complete!")
                print("\nYou can test the chat in AI Analysis Assistant now.")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("Fix ZHIPU-AI API Base URL")
    print("=" * 60)
    asyncio.run(fix_api_base())
