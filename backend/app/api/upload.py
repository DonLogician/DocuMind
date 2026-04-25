import os
import uuid
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.config import settings
from app.services.document_parser import parse_document
from app.utils.text_utils import split_text_into_chunks
from app.services.vector_service import vector_service
import aiofiles

router = APIRouter(tags=["文档上传"])


@router.post("/api/upload", summary="上传并解析文档")
async def upload_document(file: UploadFile = File(...)):
    """
    接收上传的文件，并异步完成解析。后续进度可用于向量化分块。
    """
    ext = os.path.splitext(file.filename)[1].lower()
    # 1. 验证格式支持
    if ext not in settings.ALLOWED_EXTENSIONS:
        return {
            "code": 400,
            "message": f"不支持的文件格式，仅支持: {', '.join(settings.ALLOWED_EXTENSIONS)}",
            "details": {"filename": file.filename},
            "timestamp": datetime.now().isoformat(),
        }

    # 2. 生成本地唯一存储路径
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    doc_id = str(uuid.uuid4())
    safe_filename = f"{doc_id}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    # 3. 异步流式写入大文件
    try:
        file_size = 0
        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await file.read(
                1024 * 1024
            ):  # 使用 1MB 的块大小来节省内存
                file_size += len(content)
                if file_size > settings.MAX_FILE_SIZE:
                    raise ValueError(
                        f"文件大小超出限制的 {settings.MAX_FILE_SIZE} 字节 (10MB)"
                    )
                await out_file.write(content)
    except ValueError as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {
            "code": 400,
            "message": str(e),
            "details": {"filename": file.filename},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "code": 500,
            "message": "文件保存失败, 服务器内部错误",
            "details": {"error": str(e)},
            "timestamp": datetime.now().isoformat(),
        }

    # 4. 解析与向量处理 (在 Day 2 我们将对文本分块然后入库)。
    # 注: 当处理大型文档(百兆级)时可将下面逻辑交给 FastAPI BackgroundTasks 进行离线处理
    try:
        # A. 提取纯本文
        raw_text = await parse_document(file_path, ext)

        # B. 文本分段
        chunks = split_text_into_chunks(raw_text, chunk_size=1000, chunk_overlap=200)

        # C. 向量化并持久化到 Chroma (这里加入必要的 Metadata 可在搜索时使用)
        await vector_service.add_documents(
            chunks=chunks,
            metadata={"doc_id": doc_id, "filename": file.filename, "extension": ext},
        )

        return {
            "code": 200,
            "message": "success",
            "data": {
                "doc_id": doc_id,
                "filename": file.filename,
                "content_length": len(raw_text),
                "chunks_count": len(chunks),
                "status": "embedded",
                # 前一百个字符作为预览
                "preview": raw_text[:100] + "..." if len(raw_text) > 100 else raw_text,
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        # 解析或建模发生致命错误，删除无效的文档防止积压
        if os.path.exists(file_path):
            os.remove(file_path)
        return {
            "code": 500,
            "message": "文档解析失败，内部错误",
            "details": {"error": str(e)},
            "timestamp": datetime.now().isoformat(),
        }
