from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    query: str = Field(..., description="用户输入的问题")
    session_id: Optional[str] = Field(
        None, description="当前的会话ID，用于多轮对话(基础对话可选)"
    )
    doc_id: Optional[str] = Field(
        None, description="要进行研讨的目标文档ID，用于划定检索范围"
    )


class DeepDiscussRequest(BaseModel):
    query: str = Field(..., description="用户的深层次研讨指令或问题")
    session_id: Optional[str] = Field(
        None, description="研讨会话的ID，用于长期状态跟踪"
    )
    doc_id: str = Field(..., description="必须提供的深度研讨目标文档ID")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="模型返回的回答")
    session_id: Optional[str] = Field(None, description="会话ID")
    source_documents: Optional[List[Dict[str, Any]]] = Field(
        None, description="引用的文档片段(原文)"
    )
