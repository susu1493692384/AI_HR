"""
修复已上传简历的 parsed_content 字段
将 extracted_text 复制到 parsed_content 中
"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text, update

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ai_hr"

async def fix_resume_parsed_content():
    """修复简历的 parsed_content 字段"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            print("[INFO] 开始修复简历 parsed_content 字段...")
            print()

            # 查询所有有 extracted_text 但 parsed_content 为空的简历
            result = await session.execute(
                text("""
                    SELECT id, filename, extracted_text, parsed_content
                    FROM resumes
                    WHERE extracted_text IS NOT NULL
                    AND (parsed_content IS NULL OR parsed_content = '{}'::jsonb)
                """)
            resumes = result.fetchall()

            print(f"[INFO] 找到 {len(resumes)} 份需要修复的简历")
            print()

            fixed_count = 0
            for resume in resumes:
                resume_id = resume[0]
                filename = resume[1]
                extracted_text = resume[2]
                parsed_content = resume[3]

                # 构建 parsed_content
                new_parsed_content = {
                    "extracted_text": extracted_text,
                }

                # 如果 parsed_content 已有其他数据，保留它们
                if parsed_content and isinstance(parsed_content, dict):
                    if "extracted_text" not in parsed_content:
                        new_parsed_content.update(parsed_content)

                # 更新数据库
                await session.execute(
                    text("""
                        UPDATE resumes
                        SET parsed_content = :parsed_content
                        WHERE id = :id
                    """),
                    {
                        "id": resume_id,
                        "parsed_content": new_parsed_content
                    }
                )
                print(f"  [OK] Fixed: {filename}")
                fixed_count += 1

            await session.commit()
            print()
            print(f"[SUCCESS] Fixed {fixed_count} resumes")

            # 验证
            print()
            print("[INFO] Verification:")
            result = await session.execute(
                text("""
                    SELECT COUNT(*)
                    FROM resumes
                    WHERE extracted_text IS NOT NULL
                    AND (parsed_content IS NOT NULL AND parsed_content != '{}'::jsonb)
                """)
            )
            count = result.scalar()
            print(f"  简历总数（有 extracted_text 和 parsed_content）: {count}")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("=" * 70)
    print("Fix Resume parsed_content Field")
    print("=" * 70)
    print()
    asyncio.run(fix_resume_parsed_content())
