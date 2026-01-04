"""
添加更多智谱AI模型到数据库
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
DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"

# 智谱AI模型列表
ZHIPU_MODELS = [
    {
        "llm_name": "glm-4",
        "model_type": "chat",
        "description": "最新旗舰模型，综合能力强",
        "max_tokens": 128000
    },
    {
        "llm_name": "glm-4-flash",
        "model_type": "chat",
        "description": "快速响应，成本低",
        "max_tokens": 128000
    },
    {
        "llm_name": "glm-4-plus",
        "model_type": "chat",
        "description": "增强版，能力更强",
        "max_tokens": 128000
    },
    {
        "llm_name": "glm-4-air",
        "model_type": "chat",
        "description": "轻量版，性价比高",
        "max_tokens": 128000
    },
    {
        "llm_name": "glm-3-turbo",
        "model_type": "chat",
        "description": "上一代模型，速度快",
        "max_tokens": 128000
    },
]

async def get_user_tenant_id(session: AsyncSession) -> str:
    """获取第一个用户ID作为租户ID"""
    result = await session.execute(text("SELECT id FROM users LIMIT 1"))
    user = result.fetchone()
    return user[0] if user else None

async def add_zhipu_models():
    """添加智谱AI模型"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # 获取用户租户ID
            user_tenant_id = await get_user_tenant_id(session)
            if not user_tenant_id:
                print("[ERROR] User not found")
                return

            print(f"[INFO] User Tenant ID: {user_tenant_id}")
            print(f"[INFO] Default Tenant ID: {DEFAULT_TENANT_ID}\n")

            # 获取默认租户的 ZHIPU-AI API 配置
            result = await session.execute(
                text("""
                    SELECT api_key, api_base
                    FROM tenant_llm
                    WHERE tenant_id = :default_tenant
                    AND llm_factory = 'ZHIPU-AI'
                    LIMIT 1
                """),
                {"default_tenant": DEFAULT_TENANT_ID}
            )
            config = result.fetchone()

            if not config:
                print("[ERROR] No ZHIPU-AI configuration found in default tenant")
                return

            api_key, api_base = config[0], config[1]
            print(f"[INFO] API Base: {api_base}")
            print(f"[INFO] API Key: {api_key[:20]}...\n")

            # 添加模型到默认租户
            print("[INFO] Adding models to default tenant...")
            for model_info in ZHIPU_MODELS:
                # 检查是否已存在
                result = await session.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM tenant_llm
                        WHERE tenant_id = :tenant_id
                        AND llm_factory = 'ZHIPU-AI'
                        AND llm_name = :llm_name
                    """),
                    {
                        "tenant_id": DEFAULT_TENANT_ID,
                        "llm_name": model_info["llm_name"]
                    }
                )
                exists = result.scalar()

                if exists:
                    print(f"  [SKIP] {model_info['llm_name']} - already exists")
                    continue

                await session.execute(
                    text("""
                        INSERT INTO tenant_llm
                        (tenant_id, llm_factory, model_type, llm_name, api_key, api_base, max_tokens, used_tokens, status)
                        VALUES (:tenant_id, 'ZHIPU-AI', :model_type, :llm_name, :api_key, :api_base, :max_tokens, 0, '1')
                    """),
                    {
                        "tenant_id": DEFAULT_TENANT_ID,
                        "model_type": model_info["model_type"],
                        "llm_name": model_info["llm_name"],
                        "api_key": api_key,
                        "api_base": api_base,
                        "max_tokens": model_info["max_tokens"]
                    }
                )
                print(f"  [OK] {model_info['llm_name']} - {model_info['description']}")

            # 复制到用户租户
            print(f"\n[INFO] Copying models to user tenant...")

            # 删除用户租户的旧配置
            await session.execute(
                text("DELETE FROM tenant_llm WHERE tenant_id = :user_tenant AND llm_factory = 'ZHIPU-AI'"),
                {"user_tenant": user_tenant_id}
            )

            # 复制所有模型
            result = await session.execute(
                text("""
                    SELECT llm_factory, model_type, llm_name, api_key, api_base, max_tokens
                    FROM tenant_llm
                    WHERE tenant_id = :default_tenant
                    AND llm_factory = 'ZHIPU-AI'
                """),
                {"default_tenant": DEFAULT_TENANT_ID}
            )
            models = result.fetchall()

            for model in models:
                await session.execute(
                    text("""
                        INSERT INTO tenant_llm
                        (tenant_id, llm_factory, model_type, llm_name, api_key, api_base, max_tokens, used_tokens, status)
                        VALUES (:tenant_id, :llm_factory, :model_type, :llm_name, :api_key, :api_base, :max_tokens, 0, '1')
                    """),
                    {
                        "tenant_id": user_tenant_id,
                        "llm_factory": model[0],
                        "model_type": model[1],
                        "llm_name": model[2],
                        "api_key": model[3],
                        "api_base": model[4],
                        "max_tokens": model[5]
                    }
                )

            print(f"  [OK] Copied {len(models)} models to user tenant")

            # 提交更改
            await session.commit()
            print("\n[SUCCESS] Models added successfully!")

            # 验证
            print("\n[INFO] Verification:")
            result = await session.execute(
                text("""
                    SELECT llm_name, model_type, max_tokens
                    FROM tenant_llm
                    WHERE tenant_id = :user_tenant
                    AND llm_factory = 'ZHIPU-AI'
                    ORDER BY llm_name
                """),
                {"user_tenant": user_tenant_id}
            )
            models = result.fetchall()

            print(f"\n  User tenant has {len(models)} ZHIPU-AI model(s):")
            for m in models:
                print(f"    - {m[0]} ({m[1]}) - max_tokens: {m[2]}")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("=" * 70)
    print("Add ZHIPU-AI Models")
    print("=" * 70)
    asyncio.run(add_zhipu_models())
