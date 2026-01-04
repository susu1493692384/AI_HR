#!/usr/bin/env python3
"""运行数据库初始化"""

import sys
import os
import asyncio

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db_init import init_database

if __name__ == "__main__":
    asyncio.run(init_database())