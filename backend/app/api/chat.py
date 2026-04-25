from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import llm_service
import uuid

router = APIRouter(tags=["对话"])


@router.post("/api/chat", summary="基础对话接口")
async def basic_chat(request: ChatRequest):
    """
    接收用户输入并调用通义千问大模型进行简单的、不带有上下文记忆的基础问答。
    """
    try:
        # 获取基础单轮对话回答
        answer = await llm_service.generate_basic_chat(request.query)

        # 组装返回的 Session ID (基础对话不强需求此 ID，仅作返回演示)
        session_id = request.session_id or str(uuid.uuid4())

        return {
            "code": 200,
            "message": "success",
            "data": {"answer": answer, "session_id": session_id},
            "timestamp": datetime.now().isoformat(),
        }

    except ValueError as ve:
        # LLM 模型未正确初始化等错误
        return {
            "code": 500,
            "message": "AI 服务配置有误不可用",
            "details": {"error": str(ve)},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "code": 500,
            "message": "基于大模型生成回答失败",
            "details": {"error": str(e)},
            "timestamp": datetime.now().isoformat(),
        }
