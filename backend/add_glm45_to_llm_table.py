"""
添加GLM-4.5系列模型到llm表
"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import asyncio
import uuid

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ai_hr"

GLM_45_MODELS = [
    {"llm_name": "glm-4.5", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
    {"llm_name": "glm-4.5-plus", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
    {"llm_name": "glm-4.5-air", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
    {"llm_name": "glm-4.5-flash", "model_type": "chat", "max_tokens": 128000, "tags": "LLM", "is_tools": True},
]

async def add_glm45_models():
    """添加GLM-4.5模型到llm表"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            print("[INFO] 开始添加GLM-4.5系列模型到llm表...")
            print()

            added_count = 0
            for model_info in GLM_45_MODELS:
                # 检查是否已存在
                result = await session.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM llm
                        WHERE fid = :fid
                        AND llm_name = :llm_name
                    """),
                    {"fid": "ZHIPU-AI", "llm_name": model_info["llm_name"]}
                )
                exists = result.scalar()

                if exists:
                    print(f"  [SKIP] {model_info['llm_name']} - already exists")
                    continue

                # 添加新模型（使用UUID）
                await session.execute(
                    text("""
                        INSERT INTO llm
                        (id, fid, llm_name, model_type, max_tokens, tags, is_tools, status)
                        VALUES (:id, :fid, :llm_name, :model_type, :max_tokens, :tags, :is_tools, '1')
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "fid": "ZHIPU-AI",
                        "llm_name": model_info["llm_name"],
                        "model_type": model_info["model_type"],
                        "max_tokens": model_info["max_tokens"],
                        "tags": model_info["tags"],
                        "is_tools": model_info["is_tools"],
                    }
                )
                print(f"  [OK] Added: {model_info['llm_name']}")
                added_count += 1

            await session.commit()
            print()
            print(f"[SUCCESS] Added {added_count} new models")

            # 验证
            print()
            print("[INFO] Verification:")
            result = await session.execute(
                text("""
                    SELECT llm_name, model_type
                    FROM llm
                    WHERE fid = 'ZHIPU-AI'
                    AND model_type = 'chat'
                    ORDER BY llm_name
                """)
            )
            models = result.fetchall()

            print(f"\n  Total chat models: {len(models)}")
            for m in models:
                is_45 = "✨" if "4.5" in m[0] else "  "
                print(f"    {is_45} {m[0]}")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("=" * 70)
    print("Add GLM-4.5 Models to llm table")
    print("=" * 70)
    print()
    asyncio.run(add_glm45_models())
