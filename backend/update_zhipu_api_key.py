"""
更新智谱AI的API密钥
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

def update_api_key(new_api_key: str):
    """更新智谱AI的API密钥"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 获取用户租户ID
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        if not user_result:
            print("[ERROR] No user found")
            return
        user_tenant_id = user_result['id']

        print(f"[INFO] User Tenant ID: {user_tenant_id}")
        print(f"[INFO] New API Key: {new_api_key[:20]}...{new_api_key[-6:]}")
        print()

        # 更新默认租户的所有智谱AI模型
        cursor.execute(
            """
            UPDATE tenant_llm
            SET api_key = %s
            WHERE tenant_id = %s
            AND llm_factory = 'ZHIPU-AI'
            """,
            (new_api_key, DEFAULT_TENANT_ID)
        )
        default_count = cursor.rowcount
        print(f"[OK] Updated {default_count} model(s) in default tenant")

        # 更新用户租户的所有智谱AI模型
        cursor.execute(
            """
            UPDATE tenant_llm
            SET api_key = %s
            WHERE tenant_id = %s
            AND llm_factory = 'ZHIPU-AI'
            """,
            (new_api_key, user_tenant_id)
        )
        user_count = cursor.rowcount
        print(f"[OK] Updated {user_count} model(s) in user tenant")

        conn.commit()
        print()
        print("[SUCCESS] API key updated successfully!")

        # 验证更新
        print()
        print("[INFO] Verification:")
        cursor.execute(
            """
            SELECT llm_name, api_key
            FROM tenant_llm
            WHERE tenant_id = %s
            AND llm_factory = 'ZHIPU-AI'
            LIMIT 1
            """,
            (user_tenant_id,)
        )
        result = cursor.fetchone()
        if result:
            print(f"  Model: {result['llm_name']}")
            print(f"  API Key: {result['api_key'][:20]}...{result['api_key'][-6:] if result['api_key'] else '(empty)'}")

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
    print("Update ZHIPU-AI API Key")
    print("=" * 70)
    print()

    # 获取新的API密钥
    print("请输入你的智谱AI API密钥:")
    print("获取地址: https://open.bigmodel.cn/usercenter/apikeys")
    print()

    new_key = input("API Key: ").strip()

    if not new_key:
        print("[ERROR] API Key cannot be empty")
        sys.exit(1)

    if len(new_key) < 20:
        print("[WARN] API Key seems too short. Please check and try again.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            sys.exit(0)

    update_api_key(new_key)
