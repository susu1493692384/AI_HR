"""
测试智谱AI API密钥是否有效
"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import json

def test_api_key(api_key: str):
    """测试API密钥"""
    print(f"测试API密钥: {api_key[:20]}...{api_key[-6:]}")
    print()

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "glm-4-flash",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 10
    }

    print("发送测试请求...")
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)

        print(f"HTTP状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ API密钥有效！")
            print()
            print("响应:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return True
        elif response.status_code == 401:
            print("❌ API密钥无效或已过期")
            print()
            print("错误信息:")
            print(response.text)
            return False
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print()
            print("错误信息:")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("测试智谱AI API密钥")
    print("=" * 60)
    print()

    # 从命令行获取API密钥
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("请输入智谱AI API密钥: ").strip()

    if not api_key:
        print("[ERROR] API密钥不能为空")
        sys.exit(1)

    test_api_key(api_key)
