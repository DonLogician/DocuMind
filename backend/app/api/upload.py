import os
import uuid
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.config import settings
from app.services.document_parser import parse_document
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

    # 4. 解析文档。
    # 这里如果处理时间超过 30 秒应转入 BackgroundTasks，但根据需求，这里先进行同步测试：
    try:
        raw_text = await parse_document(file_path, ext)
        # 根据 Day 1，我们只要成功验证了提取到纯文本，这一步算成功完成
        return {
            "code": 200,
            "message": "success",
            "data": {
                "doc_id": doc_id,
                "filename": file.filename,
                "content_length": len(raw_text),
                "status": "parsed",
                # 前一百个字符作为验证缩略预览
                "preview": raw_text[:100] + "..." if len(raw_text) > 100 else raw_text,
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        # 解析发生致命错误，删除无效的文档防止积压
        if os.path.exists(file_path):
            os.remove(file_path)
        return {
            "code": 500,
            "message": "文档解析失败，内部错误",
            "details": {"error": str(e)},
            "timestamp": datetime.now().isoformat(),
        }
