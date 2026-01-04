"""
检查用户租户配置
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

async def check_user_tenant():
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

            # 检查用户租户的默认模型设置
            result = await session.execute(
                text("SELECT llm_id FROM tenants WHERE id = :user_tenant"),
                {"user_tenant": user_tenant_id}
            )
            tenant = result.fetchone()
            if tenant:
                print(f"[INFO] Current LLM ID: {tenant[0] or 'NOT SET'}")

            # 检查用户租户的模型配置
            result = await session.execute(
                text("""
                    SELECT llm_factory, llm_name, model_type, status
                    FROM tenant_llm
                    WHERE tenant_id = :user_tenant
                """),
                {"user_tenant": user_tenant_id}
            )
            models = result.fetchall()

            if models:
                print(f"\n[INFO] User tenant has {len(models)} model configuration(s):")
                for m in models:
                    print(f"  - {m[0]}: {m[1]} (type: {m[2]}, status: {m[3]})")
            else:
                print("\n[WARN] User tenant has NO model configurations!")
                print("[ACTION] Need to copy models from default tenant...")

                # 从默认租户复制
                default_tenant = "00000000-0000-0000-0000-000000000001"
                result = await session.execute(
                    text("""
                        SELECT llm_factory, llm_name, model_type, api_key, api_base, max_tokens
                        FROM tenant_llm
                        WHERE tenant_id = :default_tenant
                    """),
                    {"default_tenant": default_tenant}
                )
                default_models = result.fetchall()

                if default_models:
                    print(f"\n[INFO] Found {len(default_models)} model(s) in default tenant")
                    for model in default_models:
                        # 插入到用户租户
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
                        print(f"  [OK] Copied: {model[0]} - {model[1]}")

                    # 更新默认模型
                    await session.execute(
                        text("UPDATE tenants SET llm_id = 'glm-4@ZHIPU-AI' WHERE id = :user_tenant"),
                        {"user_tenant": user_tenant_id}
                    )
                    print("\n[OK] Updated default model to: glm-4@ZHIPU-AI")

                    await session.commit()
                    print("\n[SUCCESS] User tenant configuration complete!")
                else:
                    print("[ERROR] Default tenant has no models either!")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("Check User Tenant Configuration")
    print("=" * 60)
    asyncio.run(check_user_tenant())
