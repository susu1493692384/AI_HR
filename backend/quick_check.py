"""
快速检查简历数据 - 使用psql命令
"""

import subprocess
import sys

def run_query(query, description):
    """运行SQL查询并显示结果"""
    print(f"\n{'='*80}")
    print(f"📊 {description}")
    print(f"{'='*80}")

    try:
        result = subprocess.run(
            ['psql', '-h', 'localhost', '-U', 'postgres', '-d', 'ai_hr', '-c', query],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
    except FileNotFoundError:
        print("❌ 未找到psql命令")
        print("💡 请安装PostgreSQL客户端工具")
        print("💡 或使用以下Docker命令:")
        print("   docker-compose exec postgres psql -U postgres -d ai_hr -c \"YOUR_QUERY\"")


def main():
    print("="*80)
    print("🔍 AI招聘系统 - 简历数据快速检查")
    print("="*80)

    queries = [
        (
            "SELECT COUNT(*) as total FROM resumes;",
            "简历总数"
        ),
        (
            "SELECT COUNT(*) as total, COUNT(resume_id) as with_resume FROM conversations;",
            "对话统计 (总数/关联简历数)"
        ),
        (
            "SELECT id, title, resume_id, created_at FROM conversations WHERE resume_id IS NOT NULL ORDER BY created_at DESC LIMIT 5;",
            "最近5个关联对话"
        ),
        (
            "SELECT id, candidate_name, filename, parsed_content IS NOT NULL as has_parsed, extracted_text IS NOT NULL as has_extracted, LENGTH(extracted_text) as text_length FROM resumes ORDER BY created_at DESC LIMIT 5;",
            "最近5份简历的数据状态"
        ),
        (
            "SELECT id, candidate_name, jsonb_object_keys(parsed_content) as keys FROM resumes WHERE parsed_content IS NOT NULL ORDER BY created_at DESC LIMIT 5;",
            "简历结构化数据字段"
        )
    ]

    for query, desc in queries:
        run_query(query, desc)

    print("\n" + "="*80)
    print("✅ 检查完成")
    print("="*80)

    print("\n📋 使用Docker命令运行相同检查:")
    print("-"*80)
    print("""
# 1. 检查简历总数
docker-compose exec postgres psql -U postgres -d ai_hr -c "SELECT COUNT(*) FROM resumes;"

# 2. 检查对话关联情况
docker-compose exec postgres psql -U postgres -d ai_hr -c "SELECT id, title, resume_id FROM conversations WHERE resume_id IS NOT NULL;"

# 3. 检查简历数据完整性
docker-compose exec postgres psql -U postgres -d ai_hr -c "SELECT id, candidate_name, parsed_content IS NOT NULL, extracted_text IS NOT NULL FROM resumes;"

# 4. 查看最新简历的parsed_content结构
docker-compose exec postgres psql -U postgres -d ai_hr -c "SELECT jsonb_object_keys(parsed_content) FROM resumes WHERE parsed_content IS NOT NULL LIMIT 1;"
    """)


if __name__ == "__main__":
    main()
