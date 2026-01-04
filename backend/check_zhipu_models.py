"""
检查数据库中的模型配置
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

async def check_models():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # 查看默认租户的所有模型
            result = await session.execute(text('''
                SELECT llm_factory, llm_name, model_type, status
                FROM tenant_llm
                WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
                ORDER BY llm_factory, llm_name
            '''))
            models = result.fetchall()

            print('默认租户的模型配置：')
            print('-' * 80)
            print(f'{"厂商":20} | {"模型名称":30} | {"类型":10} | {"状态"}')
            print('-' * 80)
            for m in models:
                print(f'{m[0]:20} | {m[1]:30} | {m[2]:10} | {m[3]}')

            # 查看 ZHIPU-AI 的所有模型
            result = await session.execute(text('''
                SELECT llm_factory, llm_name, model_type, status
                FROM tenant_llm
                WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
                AND llm_factory = 'ZHIPU-AI'
            '''))
            zhipu_models = result.fetchall()

            print(f'\nZHIPU-AI 模型数量: {len(zhipu_models)}')
            for m in zhipu_models:
                print(f'  - {m[1]} ({m[2]})')

            print('\n说明：')
            print('系统初始化时只配置了 glm-4 模型。')
            print('如果需要添加更多智谱AI模型（如 glm-4-flash, glm-4-plus, glm-3-turbo 等），')
            print('需要在系统设置中手动添加或运行初始化脚本。')

    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("=" * 80)
    print("Check Model Configuration")
    print("=" * 80)
    asyncio.run(check_models())
