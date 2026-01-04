"""
修复智谱AI配置
1. 添加缺失的GLM-4.5系列模型
2. 修复API Base URL
3. 更新API密钥
"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

DATABASE_URL = "postgresql://postgres:password@localhost:5432/ai_hr"
DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"
ZHIPU_API_BASE = "https://open.bigmodel.cn/api/paas/v4"

# 完整的智谱AI模型列表
ALL_ZHIPU_MODELS = [
    {"llm_name": "glm-3-turbo", "model_type": "chat"},
    {"llm_name": "glm-4", "model_type": "chat"},
    {"llm_name": "glm-4-air", "model_type": "chat"},
    {"llm_name": "glm-4-flash", "model_type": "chat"},
    {"llm_name": "glm-4-plus", "model_type": "chat"},
    {"llm_name": "glm-4.5", "model_type": "chat"},
    {"llm_name": "glm-4.5-air", "model_type": "chat"},
    {"llm_name": "glm-4.5-flash", "model_type": "chat"},
    {"llm_name": "glm-4.5-plus", "model_type": "chat"},
    {"llm_name": "embedding-2", "model_type": "embedding"},
    {"llm_name": "embedding-3", "model_type": "embedding"},
]

def get_user_tenant_id(cursor):
    """获取用户租户ID"""
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    return user[0] if user else None

def fix_zhipu_config(new_api_key=None):
    """修复智谱AI配置"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 获取用户租户ID
        user_tenant_id = get_user_tenant_id(cursor)
        if not user_tenant_id:
            print("[ERROR] User not found")
            return

        print(f"[INFO] User Tenant ID: {user_tenant_id}")
        print()

        # 1. 从默认租户获取API密钥（如果没有提供新的）
        if not new_api_key:
            cursor.execute(
                """
                SELECT api_key
                FROM tenant_llm
                WHERE tenant_id = %s
                AND llm_factory = 'ZHIPU-AI'
                AND api_key IS NOT NULL
                AND api_key != 'test.from.user.config'
                LIMIT 1
                """,
                (DEFAULT_TENANT_ID,)
            )
            result = cursor.fetchone()
            if result and result['api_key']:
                new_api_key = result['api_key']
                print(f"[INFO] Using API key from default tenant: {new_api_key[:20]}...")
            else:
                print("[WARN] No valid API key found in default tenant")
                new_api_key = input("Please enter your ZhipuAI API key: ").strip()
                if not new_api_key:
                    print("[ERROR] API key is required")
                    return

        print(f"[INFO] API Key: {new_api_key[:20]}...{new_api_key[-10:]}")
        print(f"[INFO] API Base: {ZHIPU_API_BASE}")
        print()

        # 2. 删除用户租户的所有旧配置
        cursor.execute(
            "DELETE FROM tenant_llm WHERE tenant_id = %s AND llm_factory = 'ZHIPU-AI'",
            (user_tenant_id,)
        )
        print(f"[OK] Cleared old ZHIPU-AI configuration")

        # 3. 添加所有模型配置
        for model_info in ALL_ZHIPU_MODELS:
            cursor.execute(
                """
                INSERT INTO tenant_llm
                (id, tenant_id, llm_factory, model_type, llm_name, api_key, api_base, max_tokens, used_tokens, status)
                VALUES (%s, %s, 'ZHIPU-AI', %s, %s, %s, %s, %s, 0, '1')
                """,
                (
                    str(uuid.uuid4()),
                    user_tenant_id,
                    model_info["model_type"],
                    model_info["llm_name"],
                    new_api_key,
                    ZHIPU_API_BASE,
                    128000 if model_info["model_type"] == "chat" else 8192
                )
            )
            print(f"[OK] Added: {model_info['llm_name']}")

        conn.commit()
        print()
        print("[SUCCESS] Configuration fixed!")
        print()

        # 4. 验证
        cursor.execute(
            """
            SELECT llm_name, model_type, api_base
            FROM tenant_llm
            WHERE tenant_id = %s
            AND llm_factory = 'ZHIPU-AI'
            ORDER BY model_type, llm_name
            """,
            (user_tenant_id,)
        )
        models = cursor.fetchall()

        chat_models = [m for m in models if m['model_type'] == 'chat']
        embedding_models = [m for m in models if m['model_type'] == 'embedding']

        print("[INFO] Verification:")
        print(f"\n  Chat Models ({len(chat_models)}):")
        for m in chat_models:
            has_base = '✓' if m['api_base'] else '✗'
            print(f"    {has_base} {m['llm_name']:<20} {m['api_base'] or '(no base URL)'}")

        print(f"\n  Embedding Models ({len(embedding_models)}):")
        for m in embedding_models:
            has_base = '✓' if m['api_base'] else '✗'
            print(f"    {has_base} {m['llm_name']:<20} {m['api_base'] or '(no base URL)'}")

        # 检查GLM-4.5系列
        has_45 = any('4.5' in m['llm_name'] for m in chat_models)
        if has_45:
            print("\n[SUCCESS] GLM-4.5 series models added!")
        else:
            print("\n[WARN] GLM-4.5 series models not found!")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 70)
    print("Fix ZHIPU-AI Configuration")
    print("=" * 70)
    print()

    # 获取API密钥（可选）
    import argparse
    parser = argparse.ArgumentParser(description='Fix ZHIPU-AI configuration')
    parser.add_argument('--api-key', help='New API key (optional)')
    args = parser.parse_args()

    fix_zhipu_config(args.api_key)
