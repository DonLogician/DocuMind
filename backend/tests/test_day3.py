import sys
import os
import asyncio
import uuid

# 添加 backend 目录到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.services.llm_service import llm_service
from app.services.vector_service import vector_service
from app.api.chat import chat_endpoint
from app.models.schemas import ChatRequest


async def main():
    print("开始测试 Day3：长会话和检索增强......")

    # 1. 模拟上传一个文档到向量库 (简单伪造一下，如果是真实环境需要实际索引)
    doc_id = "test-doc-day3"
    try:
        # 测试先添加一个简单的文档段落
        await vector_service.add_documents(
            chunks=[
                "DocuMind 是一个基于 RAG 架构的智能文档研讨系统。主要作者是神秘开发者。"
            ],
            metadata={"doc_id": doc_id, "source": "fake_doc.txt"},
        )
        print("准备测试数据成功。")
    except Exception as e:
        print(f"数据准备时可能已存在或其他信息: {e}")

    # 2. 发起第一轮对话
    session_id = str(uuid.uuid4())
    print(f"\n创建会话：{session_id}")

    req1 = ChatRequest(
        query="DocuMind 是什么？有哪些核心架构？", session_id=session_id, doc_id=doc_id
    )
    res1 = await chat_endpoint(req1)
    print("轮次 1 提问: DocuMind 是什么？有哪些核心架构？")
    print("轮次 1 回答:", res1["data"]["answer"])
    print("信息来源:", [doc["content"] for doc in res1["data"]["source_documents"]])

    # 3. 发起第二轮对话，测试上下文记忆
    req2 = ChatRequest(
        query="那么它的主要作者是谁？", session_id=session_id, doc_id=doc_id
    )
    res2 = await chat_endpoint(req2)
    print("\n轮次 2 提问: 那么它的主要作者是谁？")
    print("轮次 2 回答:", res2["data"]["answer"])


if __name__ == "__main__":
    asyncio.run(main())
