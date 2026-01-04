"""简历管理API端点"""

import logging
import os
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from app.core.dependencies import get_db, get_current_tenant_id_optional, get_current_user
from app.infrastructure.database.models import Resume, User
from app.application.services.resume_upload_service import get_upload_service
from app.application.services.embedding_service import VectorStoreService
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取简历列表（仅返回当前用户的简历）"""
    try:
        # 构建查询 - 只查询当前用户的简历
        query = select(Resume).where(Resume.uploaded_by == current_user.id)

        # 状态过滤
        if status:
            query = query.where(Resume.status == status)

        # 关键词搜索
        if keyword:
            search_pattern = f"%{keyword}%"
            query = query.where(
                or_(
                    Resume.filename.ilike(search_pattern),
                    Resume.candidate_name.ilike(search_pattern),
                    Resume.extracted_text.ilike(search_pattern),
                )
            )

        # 排序和分页
        query = query.order_by(Resume.upload_time.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        resumes = result.scalars().all()

        # 转换为响应格式
        return {
            "code": 0,
            "data": [
                {
                    "id": str(r.id),
                    "filename": r.filename,
                    "file_type": r.file_type,
                    "file_size": r.file_size,
                    "upload_time": r.upload_time.isoformat() if r.upload_time else None,
                    "status": r.status,
                    "candidate_name": r.candidate_name,
                    "candidate_email": r.candidate_email,
                    "candidate_phone": r.candidate_phone,
                    "candidate_location": r.candidate_location,
                }
                for r in resumes
            ],
            "total": len(resumes)
        }

    except Exception as e:
        logger.error(f"获取简历列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取简历列表失败: {str(e)}")


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
    current_user: User = Depends(get_current_user),
) -> Any:
    """上传简历文件（仅保存，不解析）"""
    import traceback

    try:
        logger.info(f"开始上传文件: {file.filename}, content_type: {file.content_type}, user_id: {current_user.id}")

        # 验证文件类型 - 支持更多类型的检查
        allowed_types = settings.ALLOWED_FILE_TYPES
        filename_lower = file.filename.lower() if file.filename else ""

        # 检查 content_type 或文件扩展名
        is_allowed = (
            file.content_type in allowed_types or
            any(filename_lower.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.html', '.htm'])
        )

        if not is_allowed:
            logger.warning(f"不支持的文件类型: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型，请上传 PDF、Word 文档或 HTML 文件"
            )

        # 读取文件内容
        file_content = await file.read()
        logger.info(f"文件读取完成，大小: {len(file_content)} bytes")

        # 验证文件大小
        max_size = settings.MAX_FILE_SIZE
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制（最大{max_size // 1024 // 1024}MB）"
            )

        # 仅保存文件，不进行解析
        upload_service = get_upload_service(db)
        resume = await upload_service.upload_file_only(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type,
            user_id=str(current_user.id)
        )
        logger.info(f"文件上传完成: {resume.id}")

        return {
            "code": 0,
            "data": {
                "id": str(resume.id),
                "filename": resume.filename,
                "status": resume.status,
                "file_size": resume.file_size,
            },
            "message": "文件上传成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"简历上传失败: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
        raise HTTPException(
            status_code=500,
            detail=f"简历上传失败: {str(e)}"
        )


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """下载简历文件（仅限下载当前用户上传的简历）"""
    try:
        result = await db.execute(
            select(Resume).where(
                and_(
                    Resume.id == resume_id,
                    Resume.uploaded_by == current_user.id
                )
            )
        )
        resume = result.scalar_one_or_none()

        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在或无权访问")

        if not resume.file_path or not os.path.exists(resume.file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 返回文件
        return FileResponse(
            path=resume.file_path,
            filename=resume.filename,
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载简历失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载简历失败: {str(e)}")


@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取简历详情（仅限当前用户上传的简历）"""
    try:
        result = await db.execute(
            select(Resume).where(
                and_(
                    Resume.id == resume_id,
                    Resume.uploaded_by == current_user.id
                )
            )
        )
        resume = result.scalar_one_or_none()

        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在或无权访问")

        return {
            "code": 0,
            "data": {
                "id": str(resume.id),
                "filename": resume.filename,
                "file_type": resume.file_type,
                "file_size": resume.file_size,
                "upload_time": resume.upload_time.isoformat() if resume.upload_time else None,
                "status": resume.status,
                "candidate_name": resume.candidate_name,
                "candidate_email": resume.candidate_email,
                "candidate_phone": resume.candidate_phone,
                "candidate_location": resume.candidate_location,
                "extracted_text": resume.extracted_text,
                "parsed_content": resume.parsed_content,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取简历详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取简历详情失败: {str(e)}")


@router.post("/{resume_id}/parse")
async def parse_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
) -> Any:
    """解析简历文件"""
    try:
        upload_service = get_upload_service(db)
        resume = await upload_service.parse_resume(resume_id, tenant_id)

        return {
            "code": 0,
            "data": {
                "id": str(resume.id),
                "filename": resume.filename,
                "status": resume.status,
                "candidate_name": resume.candidate_name,
                "candidate_email": resume.candidate_email,
                "candidate_phone": resume.candidate_phone,
                "candidate_location": resume.candidate_location,
                "extracted_text": resume.extracted_text,
            },
            "message": "简历解析成功"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"简历解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"简历解析失败: {str(e)}")


@router.post("/search")
async def search_resumes(
    query: str = Form(...),
    top_k: int = Form(10, ge=1, le=50),
    threshold: float = Form(0.5, ge=0, le=1),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id_optional),
) -> Any:
    """
    语义搜索简历

    基于查询文本的向量相似度搜索
    """
    try:
        # 获取所有已完成处理的简历
        result = await db.execute(
            select(Resume).where(
                and_(
                    Resume.status == "completed",
                    Resume.extracted_text.isnot(None)
                )
            )
        )
        resumes = result.scalars().all()

        if not resumes:
            return {
                "code": 0,
                "data": [],
                "message": "暂无简历数据"
            }

        # 生成查询向量
        from app.application.services.embedding_service import EmbeddingService
        embedding_service = EmbeddingService(db)
        query_vector = await embedding_service.embed_text(query, tenant_id)

        # 准备候选文档
        candidates = []
        for resume in resumes:
            embedding_str = resume.parsed_content.get("embedding") if resume.parsed_content else None
            if embedding_str:
                candidates.append({
                    "id": str(resume.id),
                    "filename": resume.filename,
                    "candidate_name": resume.candidate_name,
                    "candidate_email": resume.candidate_email,
                    "candidate_phone": resume.candidate_phone,
                    "candidate_location": resume.candidate_location,
                    "extracted_text": resume.extracted_text[:500] + "..." if resume.extracted_text and len(resume.extracted_text) > 500 else resume.extracted_text,
                    "embedding": embedding_str
                })

        # 执行向量搜索
        vector_store = VectorStoreService()
        results = await vector_store.search_similar(
            query_vector=query_vector,
            candidates=candidates,
            top_k=top_k,
            threshold=threshold
        )

        return {
            "code": 0,
            "data": [
                {
                    "id": r["id"],
                    "filename": r["filename"],
                    "candidate_name": r["candidate_name"],
                    "candidate_email": r["candidate_email"],
                    "candidate_phone": r["candidate_phone"],
                    "candidate_location": r["candidate_location"],
                    "similarity": round(r["similarity"], 3),
                    "extracted_text_preview": r["extracted_text"]
                }
                for r in results
            ],
            "total": len(results)
        }

    except Exception as e:
        logger.error(f"语义搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语义搜索失败: {str(e)}")


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """删除简历（仅限删除当前用户上传的简历）"""
    try:
        result = await db.execute(
            select(Resume).where(
                and_(
                    Resume.id == resume_id,
                    Resume.uploaded_by == current_user.id
                )
            )
        )
        resume = result.scalar_one_or_none()

        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在或无权删除")

        # 删除相关的分析记录（ResumeAnalysis）
        from app.infrastructure.database.models import ResumeAnalysis, Conversation
        from sqlalchemy import delete as sql_delete

        # 1. 删除 ResumeAnalysis 记录及其关联的 SkillMatch
        await db.execute(
            sql_delete(ResumeAnalysis).where(ResumeAnalysis.resume_id == resume_id)
        )
        logger.info(f"已删除简历 {resume_id} 的分析记录")

        # 2. 将关联的 Conversation 的 resume_id 设置为 NULL（保留对话记录）
        await db.execute(
            select(Conversation).where(Conversation.resume_id == resume_id)
        )
        conversations_result = await db.execute(
            select(Conversation).where(Conversation.resume_id == resume_id)
        )
        conversations = conversations_result.scalars().all()

        for conv in conversations:
            conv.resume_id = None
            logger.info(f"已解除对话 {conv.id} 与简历的关联")

        # 3. 删除文件
        import os
        if resume.file_path and os.path.exists(resume.file_path):
            try:
                os.remove(resume.file_path)
                logger.info(f"已删除文件: {resume.file_path}")
            except Exception as e:
                logger.warning(f"删除文件失败: {str(e)}")

        # 4. 删除数据库记录
        await db.delete(resume)
        await db.commit()

        return {
            "code": 0,
            "message": "简历删除成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除简历失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除简历失败: {str(e)}")
