import os
import logging
from typing import Optional, Dict, Any, List
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.config import settings
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        # 初始化通义千问模型
        # LangChain 默认从环境变量 DASHSCOPE_API_KEY 中读取密钥
        if settings.TONGYI_API_KEY:
            os.environ["DASHSCOPE_API_KEY"] = settings.TONGYI_API_KEY

        try:
            self.chat_model = ChatTongyi(
                model_name=settings.TONGYI_MODEL,
                temperature=0.7,
                # 可以在这里添加更多的模型参数
            )
            logger.info(f"成功初始化通义千问模型：{settings.TONGYI_MODEL}")
        except Exception as e:
            logger.error(
                f"初始化通义千问模型失败，请检查 TONGYI_API_KEY 设置: {str(e)}"
            )
            self.chat_model = None

        # 用于存储不同 session_id 的对话记忆对象 (按目标要求: 记忆长度为最新10轮等效 Token 数)
        self.session_memories: Dict[str, ConversationSummaryBufferMemory] = {}

    def get_memory(self, session_id: str) -> ConversationSummaryBufferMemory:
        """
        获取或为指定会话创建一个 ConversationSummaryBufferMemory 对象，
        设定 max_token_limit 保证上下文不会无限放大。
        2000 个 token 约等于多次多轮历史的摘要缓存。
        """
        if session_id not in self.session_memories:
            self.session_memories[session_id] = ConversationSummaryBufferMemory(
                llm=self.chat_model,
                max_token_limit=3000,  # 为了相当于保留最近的长文本上下文
                memory_key="history",  # 指定填入 prompt 中的历史参数名
                input_key="question",  # 仅将用户的当前提问作为记忆摘要输入
            )
        return self.session_memories[session_id]

    async def generate_basic_chat(self, query: str) -> str:
        """
        处理基础的无记忆单轮对话
        """
        if not self.chat_model:
            raise ValueError("LLM 模型未正确初始化，请检查 API KEY。")

        messages = [
            SystemMessage(
                content="你是一个专门用于智能文档研讨的AI助手 DocuMind。请回答用户的问题，保持专业和简洁。"
            ),
            HumanMessage(content=query),
        ]

        try:
            # 异步调用模型
            response = await self.chat_model.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"调用通义千问 API 发生错误: {str(e)}")
            raise e

    async def generate_rag_chat(self, query: str, session_id: str, doc_id: str) -> dict:
        """
        处理带文档检索与长期对话记忆的回答 (Day 3 上下文记忆系统实现)
        返回包含回答(answer)和来源片段(source_documents)的字典
        """
        if not self.chat_model:
            raise ValueError("LLM 模型未正确初始化，请检查 API KEY。")

        # 获取带摘要机制的内存对象
        memory = self.get_memory(session_id)

        # 获取针对当前单一文档的 MMR Retriever
        try:
            retriever = vector_service.get_retriever(k=4, doc_id=doc_id)
        except ValueError as e:
            raise ValueError(f"向量系统获取异常: {str(e)}")

        # 构建专用于文档研讨的 RAG 提示词模板
        prompt_template = """你是一个专门用于智能文档研讨的AI助手 DocuMind。请认真阅读以下检索到的文档片段(上下文)和之前的对话历史来回答用户的问题。
如果你不知道答案，请直接说不知道，不要试图编造答案。保持回答专业、客观、简洁的风格。

历史对话记忆:
{history}

文档片段(上下文):
{context}

用户问题:
{question}

专业回答:"""
        prompt = PromptTemplate(
            template=prompt_template, input_variables=["history", "context", "question"]
        )

        try:
            # 构建一个包含带历史记录的 RetrievalQA 链
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.chat_model,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt, "memory": memory},
            )

            # 异步执行问答任务
            res = await qa_chain.acall({"query": query})

            # 解析结果和来源
            answer = res.get("result", "")
            raw_sources = res.get("source_documents", [])

            source_documents = []
            for doc in raw_sources:
                source_documents.append(
                    {"content": doc.page_content, "metadata": doc.metadata}
                )

            return {"answer": answer, "source_documents": source_documents}
        except Exception as e:
            logger.error(f"RAG 伴随记忆系统查询发生错误: {str(e)}")
            raise e


# 实例化全局服务
llm_service = LLMService()
