"""基础仓库类"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

from app.infrastructure.database.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """基础仓库类"""

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        """
        初始化仓库

        Args:
            model: SQLAlchemy模型类
            db_session: 数据库会话
        """
        self.model = model
        self.db = db_session

    async def get(self, id: Any) -> Optional[ModelType]:
        """根据ID获取单个记录"""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """获取多个记录"""
        stmt = select(self.model)

        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    if key == "keyword" and value:
                        # 关键字搜索
                        stmt = stmt.where(
                            self.model.filename.ilike(f"%{value}%")
                        )
                    else:
                        stmt = stmt.where(getattr(self.model, key) == value)

        stmt = stmt.offset(skip).limit(limit)
        stmt = stmt.order_by(self.model.created_at.desc())

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(
        self,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        """创建新记录"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """更新记录"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def remove(self, *, id: Any) -> ModelType:
        """删除记录"""
        obj = await self.get(id)
        await self.db.delete(obj)
        await self.db.commit()
        return obj

    async def delete(self, id: Any) -> bool:
        """删除记录（返回是否成功）"""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """统计记录数量"""
        from sqlalchemy import func

        stmt = select(func.count(self.model.id))

        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    if key == "keyword" and value:
                        stmt = stmt.where(
                            self.model.filename.ilike(f"%{value}%")
                        )
                    else:
                        stmt = stmt.where(getattr(self.model, key) == value)

        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def exists(self, id: Any) -> bool:
        """检查记录是否存在"""
        stmt = select(self.model.id).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar() is not None