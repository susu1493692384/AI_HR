"""
添加更多智谱AI模型到数据库（使用同步连接）
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
    # GLM-4.5 系列 - 最新版本
    {
        "llm_name": "glm-4.5-plus",
        "model_type": "chat",
        "description": "GLM-4.5 增强版，能力更强（推荐）",
        "max_tokens": 128000
    },
    {
        "llm_name": "glm-4.5-air",
        "model_type": "chat",
        "description": "GLM-4.5 轻量版，性价比高",
        "max_tokens": 128000
    },
    {
        "llm_name": "glm-4.5-flash",
        "model_type": "chat",
        "description": "GLM-4.5 快速版，响应速度快",
        "max_tokens": 128000
    },
    {
        "llm_name": "glm-4.5",
        "model_type": "chat",
        "description": "GLM-4.5 标准版，综合能力强",
        "max_tokens": 128000
    },
    # 向量化模型
    {
        "llm_name": "embedding-2",
        "model_type": "embedding",
        "description": "向量化模型",
        "max_tokens": 8192
    },
    {
        "llm_name": "embedding-3",
        "model_type": "embedding",
        "description": "向量化模型 v3",
        "max_tokens": 8192
    },
]

def get_user_tenant_id(cursor):
    """获取第一个用户ID作为租户ID"""
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    return user['id'] if user else None

def add_zhipu_models():
    """添加智谱AI模型"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 获取用户租户ID
        user_tenant_id = get_user_tenant_id(cursor)
        if not user_tenant_id:
            print("[ERROR] User not found")
            return

        print(f"[INFO] User Tenant ID: {user_tenant_id}")
        print(f"[INFO] Default Tenant ID: {DEFAULT_TENANT_ID}\n")

        # 获取默认租户的 ZHIPU-AI API 配置
        cursor.execute(
            """
            SELECT api_key, api_base
            FROM tenant_llm
            WHERE tenant_id = %s
            AND llm_factory = 'ZHIPU-AI'
            LIMIT 1
            """,
            (DEFAULT_TENANT_ID,)
        )
        config = cursor.fetchone()

        if not config:
            print("[ERROR] No ZHIPU-AI configuration found in default tenant")
            return

        api_key = config['api_key']
        api_base = config['api_base']
        print(f"[INFO] API Base: {api_base}")
        print(f"[INFO] API Key: {api_key[:20] if api_key else '(empty)'}...\n")

        # 添加模型到默认租户
        print("[INFO] Adding models to default tenant...")
        added_count = 0
        for model_info in ZHIPU_MODELS:
            # 检查是否已存在
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM tenant_llm
                WHERE tenant_id = %s
                AND llm_factory = 'ZHIPU-AI'
                AND llm_name = %s
                """,
                (DEFAULT_TENANT_ID, model_info["llm_name"])
            )
            exists = cursor.fetchone()['count']

            if exists:
                print(f"  [SKIP] {model_info['llm_name']} - already exists")
                continue

            cursor.execute(
                """
                INSERT INTO tenant_llm
                (id, tenant_id, llm_factory, model_type, llm_name, api_key, api_base, max_tokens, used_tokens, status)
                VALUES (%s, %s, 'ZHIPU-AI', %s, %s, %s, %s, %s, 0, '1')
                """,
                (
                    str(uuid.uuid4()),
                    DEFAULT_TENANT_ID,
                    model_info["model_type"],
                    model_info["llm_name"],
                    api_key,
                    api_base,
                    model_info["max_tokens"]
                )
            )
            print(f"  [OK] {model_info['llm_name']} - {model_info['description']}")
            added_count += 1

        if added_count == 0:
            print("\n[INFO] All models already exist in default tenant")
        else:
            print(f"\n[OK] Added {added_count} new models to default tenant")

        # 复制到用户租户
        print(f"\n[INFO] Copying models to user tenant...")

        # 删除用户租户的旧配置
        cursor.execute(
            "DELETE FROM tenant_llm WHERE tenant_id = %s AND llm_factory = 'ZHIPU-AI'",
            (user_tenant_id,)
        )

        # 复制所有模型
        cursor.execute(
            """
            SELECT llm_factory, model_type, llm_name, api_key, api_base, max_tokens
            FROM tenant_llm
            WHERE tenant_id = %s
            AND llm_factory = 'ZHIPU-AI'
            """,
            (DEFAULT_TENANT_ID,)
        )
        models = cursor.fetchall()

        for model in models:
            cursor.execute(
                """
                INSERT INTO tenant_llm
                (id, tenant_id, llm_factory, model_type, llm_name, api_key, api_base, max_tokens, used_tokens, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, '1')
                """,
                (
                    str(uuid.uuid4()),
                    user_tenant_id,
                    model['llm_factory'],
                    model['model_type'],
                    model['llm_name'],
                    model['api_key'],
                    model['api_base'],
                    model['max_tokens']
                )
            )

        print(f"  [OK] Copied {len(models)} models to user tenant")

        # 提交更改
        conn.commit()
        print("\n[SUCCESS] Models added successfully!")

        # 验证
        print("\n[INFO] Verification:")
        cursor.execute(
            """
            SELECT llm_name, model_type, max_tokens
            FROM tenant_llm
            WHERE tenant_id = %s
            AND llm_factory = 'ZHIPU-AI'
            ORDER BY model_type, llm_name
            """,
            (user_tenant_id,)
        )
        models = cursor.fetchall()

        print(f"\n  User tenant has {len(models)} ZHIPU-AI model(s):")
        chat_models = [m for m in models if m['model_type'] == 'chat']
        embedding_models = [m for m in models if m['model_type'] == 'embedding']

        if chat_models:
            print(f"\n  Chat Models ({len(chat_models)}):")
            for m in chat_models:
                print(f"    - {m['llm_name']:<20} max_tokens: {m['max_tokens']}")

        if embedding_models:
            print(f"\n  Embedding Models ({len(embedding_models)}):")
            for m in embedding_models:
                print(f"    - {m['llm_name']:<20} max_tokens: {m['max_tokens']}")

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
    print("Add ZHIPU-AI Models")
    print("=" * 70)
    add_zhipu_models()
