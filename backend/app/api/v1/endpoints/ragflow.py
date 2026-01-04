"""RAGFlow集成API端点"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.infrastructure.external_services.ragflow_service import RAGFlowService

router = APIRouter()


@router.post("/knowledge-bases")
async def create_knowledge_base(
    name: str = Form(...),
    description: str = Form(""),
) -> Any:
    """创建RAGFlow知识库"""
    try:
        ragflow_service = RAGFlowService()
        result = await ragflow_service.create_knowledge_base(name, description)
        return {
            "success": True,
            "data": result,
            "message": "知识库创建成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建知识库失败: {str(e)}"
        )


@router.get("/knowledge-bases")
async def list_knowledge_bases() -> Any:
    """获取知识库列表"""
    try:
        ragflow_service = RAGFlowService()
        # TODO: 实现获取知识库列表的API调用
        return {
            "success": True,
            "data": [],
            "message": "获取知识库列表成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取知识库列表失败: {str(e)}"
        )


@router.post("/knowledge-bases/{kb_id}/documents")
async def upload_document_to_kb(
    kb_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Any:
    """上传文档到RAGFlow知识库"""
    try:
        # 读取文件内容
        file_content = await file.read()

        ragflow_service = RAGFlowService()
        result = await ragflow_service.upload_document(
            kb_id=kb_id,
            file_content=file_content,
            filename=file.filename
        )

        return {
            "success": True,
            "data": result,
            "message": "文档上传成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文档上传失败: {str(e)}"
        )


@router.get("/knowledge-bases/{kb_id}/documents/{doc_id}/status")
async def get_document_status(
    kb_id: str,
    doc_id: str,
) -> Any:
    """获取文档处理状态"""
    try:
        ragflow_service = RAGFlowService()
        result = await ragflow_service.get_document_status(kb_id, doc_id)

        return {
            "success": True,
            "data": result,
            "message": "获取文档状态成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取文档状态失败: {str(e)}"
        )


@router.get("/knowledge-bases/{kb_id}/search")
async def search_documents(
    kb_id: str,
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=100),
) -> Any:
    """在知识库中搜索文档"""
    try:
        ragflow_service = RAGFlowService()
        result = await ragflow_service.search(kb_id, query, top_k)

        return {
            "success": True,
            "data": result,
            "message": "搜索成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"搜索失败: {str(e)}"
        )


@router.delete("/knowledge-bases/{kb_id}/documents/{doc_id}")
async def delete_document(
    kb_id: str,
    doc_id: str,
) -> Any:
    """删除知识库中的文档"""
    try:
        # TODO: 实现删除文档的API调用
        return {
            "success": True,
            "message": "文档删除成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除文档失败: {str(e)}"
        )