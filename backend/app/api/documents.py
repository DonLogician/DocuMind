import os
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.config import settings
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["文档管理"])


@router.get("/api/documents", summary="获取已索引文档列表")
async def list_documents():
    """
    由于当前所有的文档元数据都挂载在 Chroma 矢量集中，
    我们通过聚合获取现有支持的所有不同 doc_id 的元数据。
    注：生产环境中，通常伴随使用 SQLite 等关系型数据库做元数据存储，此处为极简实现。
    """
    if not vector_service.vector_store:
        raise HTTPException(status_code=500, detail="向量服务未初始化")

    try:
        # 直接使用 Chroma 获取所有的集合数据（由于文档数量增长，这部分在生产应进行分页）
        all_data = vector_service.vector_store.get(include=["metadatas"])
        metadatas = all_data.get("metadatas", [])

        # 对 doc_id 进行去重汇聚
        docs_dict = {}
        for meta in metadatas:
            doc_id = meta.get("doc_id")
            if not doc_id:
                continue
            if doc_id not in docs_dict:
                docs_dict[doc_id] = {
                    "doc_id": doc_id,
                    "filename": meta.get("filename", "未知文件"),
                    "extension": meta.get("extension", ""),
                    "chunks_count": 1,
                }
            else:
                docs_dict[doc_id]["chunks_count"] += 1

        return {
            "code": 200,
            "message": "success",
            "data": {"documents": list(docs_dict.values())},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"获取文档列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取文档聚合时发生错误")


@router.delete("/api/documents/{doc_id}", summary="删除文档与索引")
async def delete_document(doc_id: str):
    """
    从向量引擎中删掉一个文档，如果存在原始文件，在硬盘上也应将其清理。
    """
    try:
        # 1. 矢量引擎删库
        success = await vector_service.delete_document(doc_id)

        # 2. 清除硬盘上的实体存储
        removed_files = []
        for ext in settings.ALLOWED_EXTENSIONS:
            safe_filename = f"{doc_id}{ext}"
            file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                removed_files.append(safe_filename)

        return {
            "code": 200,
            "message": "success",
            "data": {
                "doc_id": doc_id,
                "vector_cleared": success,
                "files_removed": removed_files,
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"清理文档数据失败 {doc_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="删除文档发生异常")
