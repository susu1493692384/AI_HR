"""
检查用户租户的API密钥配置
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

async def check_api_key():
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

            # 检查 glm-4 的配置
            result = await session.execute(
                text("""
                    SELECT llm_factory, llm_name, api_key, api_base, max_tokens, status
                    FROM tenant_llm
                    WHERE tenant_id = :user_tenant
                      AND llm_name = 'glm-4'
                      AND llm_factory = 'ZHIPU-AI'
                """),
                {"user_tenant": user_tenant_id}
            )
            config = result.fetchone()

            if config:
                print("\n[INFO] GLM-4 Configuration:")
                print(f"  Factory: {config[0]}")
                print(f"  Model: {config[1]}")
                print(f"  API Key: {'✅ SET' if config[2] else '❌ EMPTY'}")
                if config[2]:
                    # 只显示前4个和后4个字符
                    key = config[2]
                    masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
                    print(f"  Key Value: {masked}")
                print(f"  API Base: {config[3]}")
                print(f"  Max Tokens: {config[4]}")
                print(f"  Status: {config[5]}")
            else:
                print("[ERROR] GLM-4 configuration not found!")

            # 检查租户默认设置
            result = await session.execute(
                text("SELECT llm_id FROM tenants WHERE id = :user_tenant"),
                {"user_tenant": user_tenant_id}
            )
            tenant = result.fetchone()
            if tenant:
                print(f"\n[INFO] Tenant Default LLM ID: {tenant[0]}")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("Check API Key Configuration")
    print("=" * 60)
    asyncio.run(check_api_key())
