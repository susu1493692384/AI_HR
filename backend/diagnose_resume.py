"""
简历数据传递诊断脚本 (简化版)
使用原始SQL查询,避免ORM关系映射问题
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from app.core.config import settings


async def diagnose():
    """诊断简历数据传递问题"""

    # 创建数据库连接
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(database_url, echo=False)

    print("=" * 80)
    print("🔍 简历数据传递诊断报告")
    print("=" * 80)

    async with AsyncSession(engine) as session:
        # 1. 数据库概览
        print("\n📊 1. 数据库概览")
        print("-" * 80)

        result = await session.execute(text("SELECT COUNT(*) FROM resumes"))
        resume_count = result.scalar()
        print(f"✓ 简历总数: {resume_count}")

        result = await session.execute(text("SELECT COUNT(*) FROM conversations"))
        conv_count = result.scalar()
        print(f"✓ 对话总数: {conv_count}")

        # 2. 对话-简历关联情况
        print("\n🔗 2. 对话-简历关联情况")
        print("-" * 80)

        result = await session.execute(
            text("SELECT COUNT(*) FROM conversations WHERE resume_id IS NOT NULL")
        )
        linked_count = result.scalar()
        print(f"✓ 关联了简历的对话数: {linked_count}")

        if linked_count == 0:
            print("\n❌ 没有找到关联了简历的对话!")
            print("💡 建议: 请从简历库点击'AI分析'按钮来创建关联对话")
            await engine.dispose()
            return

        # 3. 获取最近的关联对话
        print("\n💬 3. 最近的关联对话详情")
        print("-" * 80)

        result = await session.execute(
            text("""
                SELECT id, title, resume_id, created_at
                FROM conversations
                WHERE resume_id IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 5
            """)
        )
        conversations = result.fetchall()

        for conv in conversations:
            conv_id, title, resume_id, created_at = conv
            print(f"\n对话ID: {conv_id}")
            print(f"  标题: {title}")
            print(f"  关联简历ID: {resume_id}")
            print(f"  创建时间: {created_at}")

            # 获取关联的简历
            result2 = await session.execute(
                text("""
                    SELECT id, candidate_name, filename,
                           parsed_content IS NOT NULL as has_parsed,
                           extracted_text IS NOT NULL as has_extracted,
                           LENGTH(extracted_text) as text_length
                    FROM resumes
                    WHERE id = :resume_id
                """),
                {"resume_id": str(resume_id)}
            )
            resume = result2.fetchone()

            if not resume:
                print(f"  ❌ 简历不存在!")
                continue

            res_id, name, filename, has_parsed, has_extracted, text_length = resume
            print(f"\n  📄 简历信息:")
            print(f"    ID: {res_id}")
            print(f"    姓名: {name or '未填写'}")
            print(f"    文件名: {filename}")
            print(f"    ✓ parsed_content存在: {'是' if has_parsed else '否'}")
            print(f"    ✓ extracted_text存在: {'是' if has_extracted else '否'}")

            if has_extracted:
                print(f"    ✓ extracted_text长度: {text_length} 字符")

            # 如果有parsed_content,查看其结构
            if has_parsed:
                result3 = await session.execute(
                    text("""
                        SELECT jsonb_object_keys(parsed_content) as keys
                        FROM resumes
                        WHERE id = :resume_id
                    """),
                    {"resume_id": str(resume_id)}
                )
                keys = [row[0] for row in result3.fetchall()]
                print(f"    ✓ 结构化数据字段: {keys}")

                # 检查关键字段
                result4 = await session.execute(
                    text("""
                        SELECT
                            parsed_content ? 'basic_info' as has_basic,
                            parsed_content ? 'work_experience' as has_work,
                            parsed_content ? 'education' as has_education,
                            parsed_content ? 'skills' as has_skills
                        FROM resumes
                        WHERE id = :resume_id
                    """),
                    {"resume_id": str(resume_id)}
                )
                row = result4.fetchone()
                if row:
                    has_basic, has_work, has_education, has_skills = row
                    print(f"      - basic_info: {'✓' if has_basic else '✗'}")
                    print(f"      - work_experience: {'✓' if has_work else '✗'}")
                    print(f"      - education: {'✓' if has_education else '✗'}")
                    print(f"      - skills: {'✓' if has_skills else '✗'}")

            # 诊断结果
            print(f"\n  🔍 诊断结果:")
            if not has_parsed and not has_extracted:
                print(f"    ❌ 严重问题: 简历既没有parsed_content也没有extracted_text!")
                print(f"    📝 建议: 检查简历上传和解析流程,尝试重新上传简历")
            elif has_parsed and not any(k in ['basic_info', 'work_experience', 'education', 'skills'] for k in []):
                print(f"    ⚠️  警告: parsed_content存在但可能缺少结构化字段!")
                print(f"    📝 建议: 检查简历解析器配置")
            else:
                print(f"    ✅ 简历数据完整,应该可以正常传递给AI")

        # 4. 检查最近的AI回复
        print("\n💬 5. 最近的AI消息检查")
        print("-" * 80)

        result = await session.execute(
            text("""
                SELECT m.id, m.role, m.content, c.resume_id
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                ORDER BY m.created_at DESC
                LIMIT 5
            """)
        )
        messages = result.fetchall()

        for msg in messages:
            msg_id, role, content, resume_id = msg
            content_preview = content[:100] if content else ""

            print(f"\n消息ID: {msg_id}")
            print(f"  角色: {role}")
            print(f"  关联简历: {'是' if resume_id else '否'}")
            print(f"  内容预览: {content_preview}...")

            if role == 'assistant' and resume_id:
                has_resume_context = any(keyword in content for keyword in ['候选人', '简历', '工作经历', '教育背景', '技能'])
                print(f"  包含简历上下文: {'✓ 是' if has_resume_context else '✗ 否'}")

                if not has_resume_context:
                    print(f"  ⚠️  警告: AI回复中似乎没有使用简历内容!")
                    print(f"  📝 这表明简历数据可能没有正确传递给AI")

    print("\n" + "=" * 80)
    print("✅ 诊断完成")
    print("=" * 80)

    print("\n📋 常见问题和解决方案:")
    print("-" * 80)
    print("""
1. **简历未被正确解析**
   症状: has_parsed=False, has_extracted=False
   解决:
   - 检查后端日志中的简历解析错误
   - 确认简历文件格式(PDF/DOC/DOCX)
   - 重新上传简历文件

2. **对话未关联简历**
   症状: linked_count=0
   解决:
   - 从简历库点击"AI分析"按钮
   - 不要直接在AI分析页面创建新对话

3. **AI未获取到简历上下文**
   症状: 简历数据完整但AI回复中无简历内容
   解决:
   - 检查后端日志,查找"智能体模式"相关日志
   - 确认后端正在运行
   - 重启后端服务

4. **调试建议**
   - 启动后端: cd backend && python -m uvicorn app.main:app --reload
   - 发送消息: "分析教育背景"
   - 观察日志输出,查找"已构建简历上下文"等关键信息
    """)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(diagnose())
