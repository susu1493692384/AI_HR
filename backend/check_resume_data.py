"""
简历数据传递诊断脚本
用于检查简历内容是否正确存储和传递到AI分析模块
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from app.infrastructure.database.models import Conversation, Resume, Message
from app.core.config import settings
import json


async def check_resume_data():
    """检查简历数据完整性"""

    # 创建数据库连接
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print("=" * 80)
    print("🔍 简历数据传递诊断报告")
    print("=" * 80)

    async with async_session() as session:
        # 1. 检查简历总数
        print("\n📊 1. 数据库概览")
        print("-" * 80)

        resume_count = await session.execute(select(func.count()).select_from(Resume))
        total_resumes = resume_count.scalar()
        print(f"简历总数: {total_resumes}")

        conversation_count = await session.execute(select(func.count()).select_from(Conversation))
        total_conversations = conversation_count.scalar()
        print(f"对话总数: {total_conversations}")

        # 2. 检查有resume_id的对话
        print("\n🔗 2. 对话-简历关联情况")
        print("-" * 80)

        linked_convs = await session.execute(
            select(func.count()).select_from(Conversation).where(Conversation.resume_id.isnot(None))
        )
        linked_count = linked_convs.scalar()
        print(f"关联了简历的对话数: {linked_count}")

        if linked_count > 0:
            # 获取最近的关联对话
            recent_convs = await session.execute(
                select(Conversation)
                .where(Conversation.resume_id.isnot(None))
                .order_by(Conversation.created_at.desc())
                .limit(5)
            )
            conversations = recent_convs.scalars().all()

            print("\n最近5个关联对话:")
            for conv in conversations:
                print(f"  - 对话ID: {conv.id}")
                print(f"    标题: {conv.title}")
                print(f"    关联简历ID: {conv.resume_id}")
                print()

            # 3. 检查这些对话关联的简历数据
            print("📄 3. 简历数据完整性检查")
            print("-" * 80)

            for conv in conversations:
                if not conv.resume_id:
                    continue

                # 获取简历
                resume_result = await session.execute(
                    select(Resume).where(Resume.id == conv.resume_id)
                )
                resume = resume_result.scalar_one_or_none()

                if not resume:
                    print(f"❌ 对话 {conv.id} 关联的简历 {conv.resume_id} 不存在!")
                    continue

                print(f"\n简历 ID: {resume.id}")
                print(f"候选人姓名: {resume.candidate_name or '未填写'}")
                print(f"文件名: {resume.filename}")

                # 检查parsed_content
                has_parsed = resume.parsed_content is not None
                print(f"  ✓ parsed_content存在: {has_parsed}")

                if has_parsed:
                    parsed = resume.parsed_content
                    if isinstance(parsed, dict):
                        keys = list(parsed.keys())
                        print(f"  ✓ 结构化数据字段: {keys}")

                        # 检查关键字段
                        has_basic_info = 'basic_info' in parsed
                        has_work = 'work_experience' in parsed
                        has_education = 'education' in parsed
                        has_skills = 'skills' in parsed

                        print(f"  ✓ basic_info: {'✓' if has_basic_info else '✗'}")
                        print(f"  ✓ work_experience: {'✓' if has_work else '✗'}")
                        print(f"  ✓ education: {'✓' if has_education else '✗'}")
                        print(f"  ✓ skills: {'✓' if has_skills else '✗'}")
                    else:
                        print(f"  ✗ parsed_content不是字典类型: {type(parsed)}")
                else:
                    print(f"  ✗ parsed_content为空!")

                # 检查extracted_text
                has_extracted = resume.extracted_text is not None
                print(f"  ✓ extracted_text存在: {has_extracted}")

                if has_extracted:
                    print(f"  ✓ extracted_text长度: {len(resume.extracted_text)} 字符")
                    print(f"  ✓ 前100字符: {resume.extracted_text[:100]}...")

                # 诊断结果
                if not has_parsed and not has_extracted:
                    print(f"\n  ❌ 严重问题: 简历既没有parsed_content也没有extracted_text!")
                    print(f"  📝 建议: 检查简历上传和解析流程")
                elif has_parsed and not any(k in resume.parsed_content for k in ['basic_info', 'work_experience', 'education', 'skills']):
                    print(f"\n  ⚠️  警告: parsed_content存在但缺少结构化字段!")
                    print(f"  📝 建议: 检查简历解析器配置")
        else:
            print("❌ 没有找到关联了简历的对话!")

        # 4. 检查最近的对话消息
        print("\n💬 4. 最近对话消息内容")
        print("-" * 80)

        recent_messages = await session.execute(
            select(Message)
            .order_by(Message.created_at.desc())
            .limit(10)
        )
        messages = recent_messages.scalars().all()

        for msg in messages:
            # 获取对话信息
            conv_result = await session.execute(
                select(Conversation).where(Conversation.id == msg.conversation_id)
            )
            conv = conv_result.scalar_one_or_none()

            has_resume = conv and conv.resume_id is not None
            print(f"\n消息 ID: {msg.id}")
            print(f"  角色: {msg.role}")
            print(f"  内容长度: {len(msg.content)} 字符")
            print(f"  关联简历: {'✓' if has_resume else '✗'}")

            if msg.role == 'assistant':
                content_preview = msg.content[:200]
                print(f"  内容预览: {content_preview}...")

                # 检查是否包含简历信息
                has_resume_context = '候选人' in msg.content or '简历' in msg.content or '工作经历' in msg.content
                print(f"  包含简历上下文: {'✓' if has_resume_context else '✗'}")

                if not has_resume_context and has_resume:
                    print(f"  ⚠️  警告: 对话关联了简历但AI回复中似乎没有使用简历内容!")

    print("\n" + "=" * 80)
    print("✅ 诊断完成")
    print("=" * 80)

    # 给出修复建议
    print("\n📋 修复建议:")
    print("-" * 80)
    print("""
如果发现简历内容没有传递给AI,可能的原因和解决方案:

1. **简历未被正确解析**
   - 检查后端日志中的简历解析错误
   - 确认简历文件格式支持(PDF/DOC/DOCX)
   - 重新上传简历文件

2. **对话未关联简历**
   - 从简历库点击"AI分析"按钮
   - 确认前端传递了resume_id参数
   - 检查数据库中Conversation表的resume_id字段

3. **AI未获取到简历上下文**
   - 检查后端日志中关于"智能体模式"或"简单模式"的日志
   - 确认parsed_content或extracted_text字段有数据
   - 查看是否有数据库查询错误

4. **调试步骤**
   - 启动后端服务,查看日志输出
   - 在AI分析页面发送消息"分析教育背景"
   - 观察后端日志中是否有简历数据加载的日志
   - 检查浏览器控制台的网络请求
    """)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_resume_data())
