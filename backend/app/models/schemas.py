from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    query: str = Field(..., description="用户输入的问题")
    session_id: Optional[str] = Field(
        None, description="当前的会话ID，用于多轮对话(基础对话可选)"
    )


class ChatResponse(BaseModel):
    answer: str = Field(..., description="模型返回的回答")
    session_id: Optional[str] = Field(None, description="会话ID")
