from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.schemas import ChatRequest, ChatResponse, DeepDiscussRequest
from app.services.llm_service import llm_service
from app.services.agent_service import agent_service
import uuid

router = APIRouter(tags=["对话"])


@router.post("/api/chat", summary="对话接口")
async def chat_endpoint(request: ChatRequest):
    """
    如果提供 doc_id ，进行基于文档上下文 RAG 和对话记忆(session_id) 的长会话聊天。
    否则降级为普通无文档单轮闲聊。
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())

        if request.doc_id:
            # Day 3：文档研讨模式（增强记忆 + 检索 RAG）
            result = await llm_service.generate_rag_chat(
                query=request.query, session_id=session_id, doc_id=request.doc_id
            )
            answer = result["answer"]
            source_documents = result.get("source_documents", [])
        else:
            # 基础单轮闲聊模式
            answer = await llm_service.generate_basic_chat(request.query)
            source_documents = []

        return {
            "code": 200,
            "message": "success",
            "data": {
                "answer": answer,
                "session_id": session_id,
                "source_documents": source_documents,
            },
            "timestamp": datetime.now().isoformat(),
        }

    except ValueError as ve:
        return {
            "code": 500,
            "message": "AI 服务配置有误不可用或向量系统异常",
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


@router.post("/api/chat/deep_discuss", summary="研讨型 Agent 深度对话接口")
async def deep_discuss_endpoint(request: DeepDiscussRequest):
    """
    Day 4: Agent 深度研讨端点。
    该接口使用 LangChain Agent 执行循环，大模型自主规划检索信息的节奏与次数，整合并产生具备深度理解的回复。
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())

        # 将用户的查询发往 AgentService 进行处理
        result = await agent_service.generate_deep_discuss(
            query=request.query, session_id=session_id, doc_id=request.doc_id
        )

        return {
            "code": 200,
            "message": "success",
            "data": {"answer": result["answer"], "session_id": session_id},
            "timestamp": datetime.now().isoformat(),
        }

    except ValueError as ve:
        return {
            "code": 500,
            "message": "Agent 服务配置或大模型权限异常",
            "details": {"error": str(ve)},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "code": 500,
            "message": "Agent 深度逻辑研讨处理中发生未知系统错误",
            "details": {"error": str(e)},
            "timestamp": datetime.now().isoformat(),
        }
